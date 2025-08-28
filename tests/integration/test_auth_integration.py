"""
Authentication Integration Tests

Tests that mirror examples/basic/auth_example.py
Validates real authentication flow with JWT tokens
"""

import pytest
import httpx


class TestAuthIntegration:
    
    async def test_auth_complete_flow(self, client: httpx.AsyncClient):
        """Test complete auth flow - mirrors auth_example.py"""
        
        # REGISTER - Create new user account
        register_data = {
            "name": "Auth Test User",
            "email": "authtest@example.com",
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == 201
        user = response.json()
        assert user["name"] == "Auth Test User"
        assert user["email"] == "authtest@example.com"
        assert "id" in user
        assert "password" not in user  # Password should never be returned
        
        # LOGIN - Get JWT token
        login_data = {
            "email": "authtest@example.com",
            "password": "testpassword123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Use token for authenticated requests
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # ME - Get current user profile
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["name"] == "Auth Test User"
        assert profile["email"] == "authtest@example.com"
        assert profile["id"] == user["id"]
        
        # LOGOUT - Logout (note: in current implementation this is just a message)
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        logout_response = response.json()
        assert "message" in logout_response
    
    async def test_register_duplicate_email(self, client: httpx.AsyncClient):
        """Test registration with duplicate email"""
        
        # Register first user
        user1 = {
            "name": "User One",
            "email": "duplicate@example.com",
            "password": "password123"
        }
        response = await client.post("/api/v1/auth/register", json=user1)
        assert response.status_code == 201
        
        # Try to register with same email
        user2 = {
            "name": "User Two",
            "email": "duplicate@example.com",  # Same email
            "password": "differentpassword"
        }
        response = await client.post("/api/v1/auth/register", json=user2)
        assert response.status_code == 400
        error = response.json()
        assert error["error_code"] == "DUPLICATE_EMAIL"
        assert "already registered" in error["detail"]
    
    async def test_login_invalid_credentials(self, client: httpx.AsyncClient):
        """Test login with invalid credentials"""
        
        # Register user first
        register_data = {
            "name": "Valid User",
            "email": "valid@example.com",
            "password": "correctpassword"
        }
        await client.post("/api/v1/auth/register", json=register_data)
        
        # Try login with wrong password
        login_data = {
            "email": "valid@example.com",
            "password": "wrongpassword"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        error = response.json()
        assert error["error_code"] == "LOGIN_FAILED"
        assert "Incorrect email or password" in error["detail"]
        
        # Try login with non-existent email
        login_data = {
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        error = response.json()
        assert error["error_code"] == "LOGIN_FAILED"
    
    async def test_protected_endpoint_without_token(self, client: httpx.AsyncClient):
        """Test accessing protected endpoint without authentication"""
        
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        error = response.json()
        assert error["error_code"] == "AUTHENTICATION_FAILED"
    
    async def test_protected_endpoint_invalid_token(self, client: httpx.AsyncClient):
        """Test accessing protected endpoint with invalid token"""
        
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        response = await client.get("/api/v1/auth/me", headers=invalid_headers)
        assert response.status_code == 401
        error = response.json()
        assert error["error_code"] == "INVALID_CREDENTIALS"
    
    async def test_protected_endpoints_require_auth(self, client: httpx.AsyncClient):
        """Test that all CRUD endpoints require authentication"""
        
        # Test user endpoints
        response = await client.get("/api/v1/users/")
        assert response.status_code == 401
        
        response = await client.post("/api/v1/users/", json={"name": "Test", "email": "test@test.com", "password": "test123"})
        assert response.status_code == 401
        
        # Test item endpoints  
        response = await client.get("/api/v1/items/")
        assert response.status_code == 401
        
        response = await client.post("/api/v1/items/", json={"name": "Test Item"})
        assert response.status_code == 401
    
    async def test_case_insensitive_email_login(self, client: httpx.AsyncClient):
        """Test that email login is case insensitive"""
        
        # Register with lowercase email
        register_data = {
            "name": "Case Test User",
            "email": "casetest@example.com",
            "password": "testpassword123"
        }
        await client.post("/api/v1/auth/register", json=register_data)
        
        # Login with different case variations
        login_variations = [
            "casetest@example.com",     # original
            "CaseTest@Example.com",     # mixed case
            "CASETEST@EXAMPLE.COM",     # uppercase
        ]
        
        for email_variation in login_variations:
            login_data = {
                "email": email_variation,
                "password": "testpassword123"
            }
            response = await client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 200, f"Failed to login with email: {email_variation}"
            token_data = response.json()
            assert "access_token" in token_data
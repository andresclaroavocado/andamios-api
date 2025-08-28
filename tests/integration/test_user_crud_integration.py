"""
User CRUD Integration Tests

Tests that mirror examples/basic/user_crud.py
Validates real API server with real HTTP calls
"""

import pytest
import httpx


class TestUserCRUDIntegration:
    
    async def test_user_crud_complete_flow(self, auth_client: httpx.AsyncClient):
        """Test complete user CRUD flow - mirrors user_crud.py example"""
        
        # CREATE - Create a new user
        create_user = {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "password": "securepassword123"
        }
        
        response = await auth_client.post("/api/v1/users/", json=create_user)
        assert response.status_code == 201
        user = response.json()
        assert user["name"] == "Alice Johnson"
        assert user["email"] == "alice@example.com"
        assert "id" in user
        assert "password" not in user  # Password should not be returned
        user_id = user["id"]
        
        # READ - Get the user by ID
        response = await auth_client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        retrieved_user = response.json()
        assert retrieved_user["id"] == user_id
        assert retrieved_user["name"] == "Alice Johnson"
        assert retrieved_user["email"] == "alice@example.com"
        
        # LIST - Get all users (should include our user)
        response = await auth_client.get("/api/v1/users/")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1
        
        # Find our user in the list
        found_user = None
        for u in users:
            if u["id"] == user_id:
                found_user = u
                break
        assert found_user is not None
        assert found_user["name"] == "Alice Johnson"
        
        # UPDATE - Update the user
        update_data = {
            "name": "Alice Smith",
            "email": "alice.smith@example.com"
        }
        
        response = await auth_client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["id"] == user_id
        assert updated_user["name"] == "Alice Smith"
        assert updated_user["email"] == "alice.smith@example.com"
        
        # Verify update persisted
        response = await auth_client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        verified_user = response.json()
        assert verified_user["name"] == "Alice Smith"
        assert verified_user["email"] == "alice.smith@example.com"
        
        # DELETE - Delete the user
        response = await auth_client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        delete_response = response.json()
        assert "message" in delete_response
        
        # Verify user is deleted
        response = await auth_client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 404
    
    async def test_user_not_found(self, auth_client: httpx.AsyncClient):
        """Test 404 error for non-existent user - mirrors error scenarios"""
        
        # Try to get non-existent user
        response = await auth_client.get("/api/v1/users/99999")
        assert response.status_code == 404
        error = response.json()
        assert error["error_code"] == "USER_NOT_FOUND"
        assert "User not found" in error["detail"]
        assert "timestamp" in error
    
    async def test_user_update_not_found(self, auth_client: httpx.AsyncClient):
        """Test 404 error when updating non-existent user"""
        
        update_data = {"name": "Updated Name"}
        response = await auth_client.put("/api/v1/users/99999", json=update_data)
        assert response.status_code == 404
        error = response.json()
        assert error["error_code"] == "USER_NOT_FOUND"
    
    async def test_user_delete_not_found(self, auth_client: httpx.AsyncClient):
        """Test 404 error when deleting non-existent user"""
        
        response = await auth_client.delete("/api/v1/users/99999")
        assert response.status_code == 404
        error = response.json()
        assert error["error_code"] == "USER_NOT_FOUND"
    
    async def test_duplicate_email_error(self, auth_client: httpx.AsyncClient):
        """Test duplicate email handling"""
        
        # Create first user
        user1 = {
            "name": "User One",
            "email": "duplicate@example.com",
            "password": "password123"
        }
        response = await auth_client.post("/api/v1/users/", json=user1)
        assert response.status_code == 201
        
        # Try to create user with same email
        user2 = {
            "name": "User Two", 
            "email": "duplicate@example.com",
            "password": "password456"
        }
        response = await auth_client.post("/api/v1/users/", json=user2)
        assert response.status_code == 400
        error = response.json()
        assert error["error_code"] == "DUPLICATE_EMAIL"
        assert "already registered" in error["detail"]
"""
Validation Integration Tests

Tests that mirror examples/basic/validation_example.py
Validates input validation and error handling
"""

import pytest
import httpx


class TestValidationIntegration:
    
    async def test_user_validation_errors(self, auth_client: httpx.AsyncClient):
        """Test user validation errors - mirrors validation_example.py"""
        
        # Invalid email format
        invalid_email_user = {
            "name": "Test User",
            "email": "not-an-email",  # Invalid format
            "password": "password123"
        }
        response = await auth_client.post("/api/v1/users/", json=invalid_email_user)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        assert len(error["validation_errors"]) > 0
        
        # Check for email validation error
        email_error = None
        for val_error in error["validation_errors"]:
            if val_error["field"] == "email":
                email_error = val_error
                break
        assert email_error is not None
        assert "email" in email_error["message"].lower()
        
        # Missing required name field
        no_name_user = {
            "email": "valid@example.com",
            "password": "password123"
            # Missing name field
        }
        response = await auth_client.post("/api/v1/users/", json=no_name_user)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        assert len(error["validation_errors"]) > 0
        
        # Missing email field
        no_email_user = {
            "name": "Test User",
            "password": "password123"
            # Missing email field
        }
        response = await auth_client.post("/api/v1/users/", json=no_email_user)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        assert len(error["validation_errors"]) > 0
        
        # Missing password field
        no_password_user = {
            "name": "Test User",
            "email": "test@example.com"
            # Missing password field
        }
        response = await auth_client.post("/api/v1/users/", json=no_password_user)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        
        # Empty name (after trimming)
        empty_name_user = {
            "name": "",  # Empty string
            "email": "empty@example.com",
            "password": "password123"
        }
        response = await auth_client.post("/api/v1/users/", json=empty_name_user)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
    
    async def test_item_validation_errors(self, auth_client: httpx.AsyncClient):
        """Test item validation errors"""
        
        # Missing required name field
        no_name_item = {
            "description": "Item without name"
            # Missing name field
        }
        response = await auth_client.post("/api/v1/items/", json=no_name_item)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        assert len(error["validation_errors"]) > 0
        
        # Check for name validation error
        name_error = None
        for val_error in error["validation_errors"]:
            if val_error["field"] == "name":
                name_error = val_error
                break
        assert name_error is not None
        
        # Empty name
        empty_name_item = {
            "name": "",  # Empty string
            "description": "Item with empty name"
        }
        response = await auth_client.post("/api/v1/items/", json=empty_name_item)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
    
    async def test_update_validation_errors(self, auth_client: httpx.AsyncClient):
        """Test update validation errors"""
        
        # Create valid user first
        valid_user = {
            "name": "Update Test",
            "email": "update.test@example.com",
            "password": "password123"
        }
        response = await auth_client.post("/api/v1/users/", json=valid_user)
        assert response.status_code == 201
        user = response.json()
        user_id = user["id"]
        
        # Empty update (no fields provided)
        response = await auth_client.put(f"/api/v1/users/{user_id}", json={})
        assert response.status_code == 400
        error = response.json()
        assert error["error_code"] == "EMPTY_UPDATE"
        
        # Invalid email in update
        invalid_update = {
            "email": "not-valid-email"  # Invalid format
        }
        response = await auth_client.put(f"/api/v1/users/{user_id}", json=invalid_update)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        assert len(error["validation_errors"]) > 0
    
    async def test_login_validation_errors(self, client: httpx.AsyncClient):
        """Test login validation errors"""
        
        # Missing email in login
        no_email_login = {
            "password": "password123"
            # Missing email field
        }
        response = await client.post("/api/v1/auth/login", json=no_email_login)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        assert len(error["validation_errors"]) > 0
        
        # Missing password in login
        no_password_login = {
            "email": "test@example.com"
            # Missing password field
        }
        response = await client.post("/api/v1/auth/login", json=no_password_login)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        assert len(error["validation_errors"]) > 0
    
    async def test_register_validation_errors(self, client: httpx.AsyncClient):
        """Test registration validation errors"""
        
        # Password too short
        short_password = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "short"  # Less than 8 characters
        }
        response = await client.post("/api/v1/auth/register", json=short_password)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        
        # Name too short
        short_name = {
            "name": "A",  # Less than 2 characters
            "email": "test@example.com",
            "password": "validpassword123"
        }
        response = await client.post("/api/v1/auth/register", json=short_name)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
        
        # Name too long
        long_name = {
            "name": "A" * 51,  # More than 50 characters
            "email": "test@example.com",
            "password": "validpassword123"
        }
        response = await client.post("/api/v1/auth/register", json=long_name)
        assert response.status_code == 422
        error = response.json()
        assert error["error_code"] == "VALIDATION_ERROR"
    
    async def test_validation_error_structure(self, auth_client: httpx.AsyncClient):
        """Test that validation errors have correct structure"""
        
        # Trigger validation error
        invalid_user = {
            "name": "",  # Empty name
            "email": "invalid-email",  # Invalid email
            "password": "short"  # Password too short
        }
        
        response = await auth_client.post("/api/v1/users/", json=invalid_user)
        assert response.status_code == 422
        error = response.json()
        
        # Check error structure
        assert "detail" in error
        assert "error_code" in error
        assert "timestamp" in error
        assert "validation_errors" in error
        assert error["error_code"] == "VALIDATION_ERROR"
        assert error["detail"] == "Validation failed"
        
        # Check validation_errors structure
        assert isinstance(error["validation_errors"], list)
        assert len(error["validation_errors"]) > 0
        
        for val_error in error["validation_errors"]:
            assert "field" in val_error or val_error["field"] is None
            assert "message" in val_error
            assert "code" in val_error
            assert isinstance(val_error["message"], str)
            assert isinstance(val_error["code"], str)
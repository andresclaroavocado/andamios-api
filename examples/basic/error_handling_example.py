"""
Error Handling Example (client-only)

Rules:
- No server/FastAPI setup here.
- Tests all error scenarios (404, 422, 500).
- Validates error response format.
- Ensures proper HTTP status codes.
"""

import asyncio
import httpx
import json

async def main():
    print("🚀 Error Handling Operations")
    
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        
        # Get auth token first for protected endpoints
        register_data = {
            "name": "Error Test User",
            "email": "error.test@example.com",
            "password": "password123"
        }
        await client.post("/api/v1/auth/register", json=register_data)
        
        login_data = {
            "email": "error.test@example.com",
            "password": "password123"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        token_data = response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        print("🔐 authenticated for error testing")
        
        # 404 ERRORS - Test not found scenarios
        print("\n📍 Testing 404 Errors")
        
        # User not found
        response = await client.get("/api/v1/users/999", headers=headers)
        print(f"   GET /users/999: {response.status_code}")        # expected: 404
        if response.status_code == 404:
            error = response.json()
            print(f"   ✅ User 404: {error['detail']}")           # expected: "User not found"
        
        # Item not found  
        response = await client.get("/api/v1/items/999", headers=headers)
        print(f"   GET /items/999: {response.status_code}")       # expected: 404
        if response.status_code == 404:
            error = response.json()
            print(f"   ✅ Item 404: {error['detail']}")           # expected: "Item not found"
        
        # Delete non-existent user
        response = await client.delete("/api/v1/users/999", headers=headers)
        print(f"   DELETE /users/999: {response.status_code}")    # expected: 404
        if response.status_code == 404:
            error = response.json()
            print(f"   ✅ Delete 404: {error['detail']}")         # expected: "User not found"
        
        # 422 ERRORS - Test validation scenarios
        print("\n📝 Testing 422 Validation Errors")
        
        # Invalid email format
        invalid_user = {
            "name": "Test User",
            "email": "invalid-email",  # Invalid format
            "password": "password123"
        }
        response = await client.post("/api/v1/users/", json=invalid_user, headers=headers)
        print(f"   POST invalid email: {response.status_code}")   # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Email validation: {len(error['detail'])} errors")  # expected: > 0
        
        # Missing required fields
        incomplete_user = {
            "email": "test@example.com"
            # Missing name and password
        }
        response = await client.post("/api/v1/users/", json=incomplete_user, headers=headers)
        print(f"   POST missing fields: {response.status_code}")  # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Missing fields: {len(error['detail'])} errors")   # expected: > 0
        
        # Empty update data
        response = await client.put("/api/v1/users/1", json={}, headers=headers)
        print(f"   PUT empty update: {response.status_code}")     # expected: 400
        if response.status_code == 400:
            error = response.json()
            print(f"   ✅ Empty update: {error['detail']}")       # expected: "No fields to update"
        
        # Missing item name
        incomplete_item = {
            "description": "Item without name"
            # Missing required name field
        }
        response = await client.post("/api/v1/items/", json=incomplete_item, headers=headers)
        print(f"   POST missing name: {response.status_code}")    # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Missing name: {len(error['detail'])} errors")     # expected: > 0
        
        # 401 ERRORS - Test authentication scenarios
        print("\n🔒 Testing 401 Authentication Errors")
        
        # No token provided
        response = await client.get("/api/v1/users/")
        print(f"   GET without token: {response.status_code}")    # expected: 401
        if response.status_code == 401:
            error = response.json()
            print(f"   ✅ No token: {error['detail']}")           # expected: "Not authenticated"
        
        # Invalid token
        bad_headers = {"Authorization": "Bearer invalid-token"}
        response = await client.get("/api/v1/users/", headers=bad_headers)
        print(f"   GET invalid token: {response.status_code}")    # expected: 401
        if response.status_code == 401:
            error = response.json()
            print(f"   ✅ Invalid token: {error['detail']}")      # expected: "Could not validate credentials"
        
        # Test login with wrong credentials
        wrong_login = {
            "email": "error.test@example.com",
            "password": "wrongpassword"
        }
        response = await client.post("/api/v1/auth/login", json=wrong_login)
        print(f"   POST wrong password: {response.status_code}")  # expected: 401
        if response.status_code == 401:
            error = response.json()
            print(f"   ✅ Wrong password: {error['detail']}")     # expected: "Incorrect email or password"

if __name__ == "__main__":
    asyncio.run(main())
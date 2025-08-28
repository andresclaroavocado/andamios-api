"""
Input Validation Example (client-only)

Rules:
- No server/FastAPI setup here.
- Tests invalid email, missing fields, length limits.
- Validates error response structure.
- Ensures proper 422 status codes.
"""

import asyncio
import httpx

async def main():
    print("🚀 Input Validation Operations")
    
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        
        # Get auth token for protected endpoints
        auth_user = {
            "name": "Validation User",
            "email": "validation@example.com",
            "password": "password123"
        }
        await client.post("/api/v1/auth/register", json=auth_user)
        
        login_data = {
            "email": "validation@example.com",
            "password": "password123"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        token_data = response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        print("🔐 authenticated for validation testing")
        
        # USER VALIDATION TESTS
        print("\n👤 Testing User Validation")
        
        # Invalid email format
        invalid_email_user = {
            "name": "Test User",
            "email": "not-an-email",  # Invalid format
            "password": "password123"
        }
        response = await client.post("/api/v1/users/", json=invalid_email_user, headers=headers)
        print(f"   Invalid email: {response.status_code}")     # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Validation errors: {len(error.get('validation_errors', []))}")  # expected: > 0
            for val_error in error.get('validation_errors', []):
                print(f"      - {val_error['field']}: {val_error['message']}")
        
        # Missing name field
        no_name_user = {
            "email": "valid@example.com",
            "password": "password123"
            # Missing required name field
        }
        response = await client.post("/api/v1/users/", json=no_name_user, headers=headers)
        print(f"   Missing name: {response.status_code}")       # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Missing field errors: {len(error.get('validation_errors', []))}")
            
        # Missing email field  
        no_email_user = {
            "name": "Test User",
            "password": "password123"
            # Missing required email field
        }
        response = await client.post("/api/v1/users/", json=no_email_user, headers=headers)
        print(f"   Missing email: {response.status_code}")      # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Missing email error: {len(error.get('validation_errors', []))}")
        
        # Missing password field
        no_password_user = {
            "name": "Test User",
            "email": "test@example.com"
            # Missing required password field
        }
        response = await client.post("/api/v1/users/", json=no_password_user, headers=headers)
        print(f"   Missing password: {response.status_code}")   # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Missing password error: {len(error.get('validation_errors', []))}")
        
        # Empty name (after trimming)
        empty_name_user = {
            "name": "",  # Empty string
            "email": "empty@example.com",
            "password": "password123"
        }
        response = await client.post("/api/v1/users/", json=empty_name_user, headers=headers)
        print(f"   Empty name: {response.status_code}")         # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Empty name error: {len(error.get('validation_errors', []))}")
        
        # ITEM VALIDATION TESTS
        print("\n📦 Testing Item Validation")
        
        # Missing name (required field)
        no_name_item = {
            "description": "Item without name"
            # Missing required name field
        }
        response = await client.post("/api/v1/items/", json=no_name_item, headers=headers)
        print(f"   Missing name: {response.status_code}")       # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Missing name error: {len(error.get('validation_errors', []))}")
            for val_error in error.get('validation_errors', []):
                print(f"      - {val_error['field']}: {val_error['message']}")
        
        # Empty name
        empty_name_item = {
            "name": "",  # Empty string
            "description": "Item with empty name"
        }
        response = await client.post("/api/v1/items/", json=empty_name_item, headers=headers)
        print(f"   Empty name: {response.status_code}")         # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Empty name error: {len(error.get('validation_errors', []))}")
        
        # UPDATE VALIDATION TESTS
        print("\n🔄 Testing Update Validation")
        
        # Create a valid user first
        valid_user = {
            "name": "Update Test",
            "email": "update.test@example.com",
            "password": "password123"
        }
        response = await client.post("/api/v1/users/", json=valid_user, headers=headers)
        if response.status_code == 201:
            user = response.json()
            user_id = user["id"]
            
            # Empty update (no fields)
            response = await client.put(f"/api/v1/users/{user_id}", json={}, headers=headers)
            print(f"   Empty update: {response.status_code}")   # expected: 400
            if response.status_code == 400:
                error = response.json()
                print(f"   ✅ Empty update: {error['error_code']}")  # expected: EMPTY_UPDATE
            
            # Invalid email in update
            invalid_update = {
                "email": "not-valid-email"  # Invalid format
            }
            response = await client.put(f"/api/v1/users/{user_id}", json=invalid_update, headers=headers)
            print(f"   Invalid email update: {response.status_code}")  # expected: 422
            if response.status_code == 422:
                error = response.json()
                print(f"   ✅ Invalid email update: {len(error.get('validation_errors', []))}")
        
        # LOGIN VALIDATION TESTS  
        print("\n🔐 Testing Login Validation")
        
        # Missing email in login
        no_email_login = {
            "password": "password123"
            # Missing email field
        }
        response = await client.post("/api/v1/auth/login", json=no_email_login)
        print(f"   Login missing email: {response.status_code}")  # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Login validation: {len(error.get('validation_errors', []))}")
        
        # Missing password in login
        no_password_login = {
            "email": "test@example.com"
            # Missing password field
        }
        response = await client.post("/api/v1/auth/login", json=no_password_login)
        print(f"   Login missing password: {response.status_code}")  # expected: 422
        if response.status_code == 422:
            error = response.json()
            print(f"   ✅ Login password validation: {len(error.get('validation_errors', []))}")

if __name__ == "__main__":
    asyncio.run(main())
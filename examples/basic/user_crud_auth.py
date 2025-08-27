"""
User CRUD with Authentication Example (client-only)

Rules:
- No server/FastAPI setup here.
- Same as user_crud.py but with JWT token in headers.
- Demonstrates protected CRUD operations.
"""

import asyncio
import httpx

async def main():
    print("🚀 User CRUD Operations with Authentication")
    
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        
        # AUTHENTICATE FIRST - Register and login
        register_data = {
            "name": "CRUD User",
            "email": "crud.user@example.com",
            "password": "password123"
        }
        await client.post("/api/v1/auth/register", json=register_data)
        
        login_data = {
            "email": "crud.user@example.com",
            "password": "password123"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        token_data = response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        print("🔐 authenticated for CRUD operations")
        
        # CREATE - with auth header
        user_data = {
            "name": "Protected User",
            "email": "protected@example.com",
            "password": "secret456"
        }
        response = await client.post("/api/v1/users/", json=user_data, headers=headers)
        user = response.json()
        print("✅ created:", user["id"], user["name"])      # expected: id != None, "Protected User"
        
        # READ - single user with auth
        response = await client.get(f"/api/v1/users/{user['id']}", headers=headers)
        found = response.json()
        print("📖 read:", found["name"])                    # expected: "Protected User"
        print("   email:", found["email"])                  # expected: "protected@example.com"
        
        # READ - all users with auth
        response = await client.get("/api/v1/users/", headers=headers)
        users = response.json()
        print("📋 all users:", len(users))                  # expected: >= 2
        
        # UPDATE - with auth header
        updated_data = {"name": "Updated Protected", "email": "updated.protected@example.com"}
        response = await client.put(f"/api/v1/users/{user['id']}", json=updated_data, headers=headers)
        updated = response.json()
        print("✏️ updated:", updated["name"], updated["email"])  # expected: "Updated Protected", "updated.protected@example.com"
        
        # DELETE - with auth header
        response = await client.delete(f"/api/v1/users/{user['id']}", headers=headers)
        result = response.json()
        print("🗑️ deleted:", result["message"])             # expected: contains user id

if __name__ == "__main__":
    asyncio.run(main())
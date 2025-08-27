"""
User CRUD Example (client-only)

Rules:
- No server/FastAPI setup here.
- No Pydantic schemas/models defined here.
- Use the API endpoints from the running server.
"""

import asyncio
import httpx

async def main():
    print("🚀 User CRUD Operations")
    
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        
        # CREATE
        user_data = {
            "name": "John Doe", 
            "email": "john.doe@example.com",
            "password": "secret123"
        }
        response = await client.post("/api/v1/users/", json=user_data)
        user = response.json()
        print("✅ created:", user["id"], user["name"])  # expected: id != None, "John Doe"
        
        # READ - single user
        response = await client.get(f"/api/v1/users/{user['id']}")
        found = response.json()
        print("📖 read:", found["name"])                # expected: "John Doe"
        print("   email:", found["email"])              # expected: "john.doe@example.com"
        
        # READ - all users
        response = await client.get("/api/v1/users/")
        users = response.json()
        print("📋 all users:", len(users))              # expected: >= 1
        
        # UPDATE (when implemented)
        # updated_data = {"name": "John Updated", "email": "john.updated@example.com"}
        # response = await client.put(f"/api/v1/users/{user['id']}", json=updated_data)
        # updated = response.json()
        # print("✏️ updated:", updated["name"], updated["email"])
        
        # DELETE
        response = await client.delete(f"/api/v1/users/{user['id']}")
        result = response.json()
        print("🗑️ deleted:", result["message"])         # expected: contains user id

if __name__ == "__main__":
    asyncio.run(main())
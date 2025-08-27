"""
Authentication Example (client-only)

Rules:
- No server/FastAPI setup here.
- No authentication logic defined here.
- Use the authentication endpoints from the running server.
"""

import asyncio
import httpx

async def main():
    print("🚀 Authentication Operations")
    
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        
        # CREATE - Register user
        register_data = {
            "name": "Auth User",
            "email": "auth.user@example.com", 
            "password": "securepass123"
        }
        response = await client.post("/api/v1/auth/register", json=register_data)
        user = response.json()
        print("✅ registered:", user["id"], user["name"])  # expected: id != None, "Auth User"
        
        # LOGIN - Get JWT token
        login_data = {
            "email": "auth.user@example.com",
            "password": "securepass123"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        print("🔐 logged in:", token_data["token_type"])    # expected: "bearer"
        
        # ACCESS - Use token for protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        profile = response.json()
        print("👤 profile:", profile["name"], profile["email"])  # expected: "Auth User", "auth.user@example.com"
        
        # ACCESS - Test protected CRUD endpoint
        response = await client.get("/api/v1/users/", headers=headers)
        users = response.json()
        print("📋 protected users:", len(users))            # expected: >= 1
        
        # LOGOUT - Invalidate token
        response = await client.post("/api/v1/auth/logout", headers=headers)
        logout_result = response.json()
        print("🚪 logged out:", logout_result["message"])   # expected: contains "logged out"

if __name__ == "__main__":
    asyncio.run(main())
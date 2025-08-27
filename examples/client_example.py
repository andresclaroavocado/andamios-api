import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Health check
        response = await client.get("/health")
        print("Health check:", response.json())
        
        # Create user
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "secret123"
        }
        response = await client.post("/api/v1/users/", json=user_data)
        print("Created user:", response.json())
        
        # Get users
        response = await client.get("/api/v1/users/")
        print("Users:", response.json())
        
        # Create item
        item_data = {
            "name": "Test Item",
            "description": "A test item"
        }
        response = await client.post("/api/v1/items/", json=item_data)
        print("Created item:", response.json())

if __name__ == "__main__":
    asyncio.run(main())
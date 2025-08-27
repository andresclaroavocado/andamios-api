"""
Item CRUD Example (client-only)

Rules:
- No server/FastAPI setup here.
- No Pydantic schemas/models defined here.
- Use the API endpoints from the running server.
"""

import asyncio
import httpx

async def main():
    print("🚀 Item CRUD Operations")
    
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        
        # CREATE
        item_data = {
            "name": "My Task",
            "description": "Important project task"
        }
        response = await client.post("/api/v1/items/", json=item_data)
        item = response.json()
        print("✅ created:", item["id"], item["name"])   # expected: id != None, "My Task"
        
        # READ - single item
        response = await client.get(f"/api/v1/items/{item['id']}")
        found = response.json()
        print("📖 read:", found["name"])                 # expected: "My Task"
        print("   description:", found["description"])   # expected: "Important project task"
        
        # READ - all items
        response = await client.get("/api/v1/items/")
        items = response.json()
        print("📋 all items:", len(items))               # expected: >= 1
        
        # UPDATE
        updated_data = {"name": "Updated Task", "description": "Updated description"}
        response = await client.put(f"/api/v1/items/{item['id']}", json=updated_data)
        updated = response.json()
        print("✏️ updated:", updated["name"], updated["description"])  # expected: "Updated Task", "Updated description"
        
        # DELETE
        response = await client.delete(f"/api/v1/items/{item['id']}")
        result = response.json()
        print("🗑️ deleted:", result["message"])          # expected: contains item id

if __name__ == "__main__":
    asyncio.run(main())
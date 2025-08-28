"""
Item CRUD Integration Tests

Tests that mirror examples/basic/item_crud.py
Validates real API server with real HTTP calls
"""

import pytest
import httpx


class TestItemCRUDIntegration:
    
    async def test_item_crud_complete_flow(self, auth_client: httpx.AsyncClient):
        """Test complete item CRUD flow - mirrors item_crud.py example"""
        
        # CREATE - Create a new item
        create_item = {
            "name": "Test Item",
            "description": "A sample item for testing"
        }
        
        response = await auth_client.post("/api/v1/items/", json=create_item)
        assert response.status_code == 201
        item = response.json()
        assert item["name"] == "Test Item"
        assert item["description"] == "A sample item for testing"
        assert "id" in item
        item_id = item["id"]
        
        # READ - Get the item by ID
        response = await auth_client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        retrieved_item = response.json()
        assert retrieved_item["id"] == item_id
        assert retrieved_item["name"] == "Test Item"
        assert retrieved_item["description"] == "A sample item for testing"
        
        # LIST - Get all items (should include our item)
        response = await auth_client.get("/api/v1/items/")
        assert response.status_code == 200
        items = response.json()
        assert isinstance(items, list)
        assert len(items) >= 1
        
        # Find our item in the list
        found_item = None
        for i in items:
            if i["id"] == item_id:
                found_item = i
                break
        assert found_item is not None
        assert found_item["name"] == "Test Item"
        
        # UPDATE - Update the item
        update_data = {
            "name": "Updated Test Item",
            "description": "An updated sample item"
        }
        
        response = await auth_client.put(f"/api/v1/items/{item_id}", json=update_data)
        assert response.status_code == 200
        updated_item = response.json()
        assert updated_item["id"] == item_id
        assert updated_item["name"] == "Updated Test Item"
        assert updated_item["description"] == "An updated sample item"
        
        # Verify update persisted
        response = await auth_client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        verified_item = response.json()
        assert verified_item["name"] == "Updated Test Item"
        assert verified_item["description"] == "An updated sample item"
        
        # DELETE - Delete the item
        response = await auth_client.delete(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        delete_response = response.json()
        assert "message" in delete_response
        
        # Verify item is deleted
        response = await auth_client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 404
    
    async def test_item_without_description(self, auth_client: httpx.AsyncClient):
        """Test creating item without description - should work with None"""
        
        create_item = {
            "name": "Item Without Description"
            # No description field
        }
        
        response = await auth_client.post("/api/v1/items/", json=create_item)
        assert response.status_code == 201
        item = response.json()
        assert item["name"] == "Item Without Description"
        assert item["description"] is None
    
    async def test_item_with_empty_description(self, auth_client: httpx.AsyncClient):
        """Test creating item with empty description - should convert to None"""
        
        create_item = {
            "name": "Item With Empty Description",
            "description": ""
        }
        
        response = await auth_client.post("/api/v1/items/", json=create_item)
        assert response.status_code == 201
        item = response.json()
        assert item["name"] == "Item With Empty Description"
        assert item["description"] is None
    
    async def test_item_not_found(self, auth_client: httpx.AsyncClient):
        """Test 404 error for non-existent item - mirrors error scenarios"""
        
        # Try to get non-existent item
        response = await auth_client.get("/api/v1/items/99999")
        assert response.status_code == 404
        error = response.json()
        assert error["error_code"] == "ITEM_NOT_FOUND"
        assert "Item not found" in error["detail"]
        assert "timestamp" in error
    
    async def test_item_update_not_found(self, auth_client: httpx.AsyncClient):
        """Test 404 error when updating non-existent item"""
        
        update_data = {"name": "Updated Name"}
        response = await auth_client.put("/api/v1/items/99999", json=update_data)
        assert response.status_code == 404
        error = response.json()
        assert error["error_code"] == "ITEM_NOT_FOUND"
    
    async def test_item_delete_not_found(self, auth_client: httpx.AsyncClient):
        """Test 404 error when deleting non-existent item"""
        
        response = await auth_client.delete("/api/v1/items/99999")
        assert response.status_code == 404
        error = response.json()
        assert error["error_code"] == "ITEM_NOT_FOUND"
    
    async def test_partial_item_update(self, auth_client: httpx.AsyncClient):
        """Test updating only some fields of an item"""
        
        # Create item
        create_item = {
            "name": "Original Name",
            "description": "Original description"
        }
        response = await auth_client.post("/api/v1/items/", json=create_item)
        assert response.status_code == 201
        item = response.json()
        item_id = item["id"]
        
        # Update only name
        update_data = {"name": "New Name"}
        response = await auth_client.put(f"/api/v1/items/{item_id}", json=update_data)
        assert response.status_code == 200
        updated_item = response.json()
        assert updated_item["name"] == "New Name"
        assert updated_item["description"] == "Original description"  # Should remain unchanged
        
        # Update only description
        update_data = {"description": "New description"}
        response = await auth_client.put(f"/api/v1/items/{item_id}", json=update_data)
        assert response.status_code == 200
        updated_item = response.json()
        assert updated_item["name"] == "New Name"  # Should remain unchanged
        assert updated_item["description"] == "New description"
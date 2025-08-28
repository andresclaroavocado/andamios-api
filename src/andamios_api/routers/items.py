from fastapi import APIRouter, HTTPException, Depends
from typing import List
from andamios_api.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from andamios_api.models.item import Item
from andamios_api.routers.auth import get_current_user
from andamios_api.models.user import User

router = APIRouter()

@router.get("/", response_model=List[ItemResponse],
           summary="List all items",
           description="""
           Retrieve a list of all items in the system.
           
           Example from `examples/basic/item_crud.py`:
           ```python
           response = await client.get("/api/v1/items/", headers=auth_headers)
           items = response.json()
           ```
           
           **Requires**: Valid JWT token in Authorization header.
           """,
           responses={
               200: {"description": "List of items retrieved successfully"},
               401: {"description": "Authentication required"}
           })
async def get_items(current_user: User = Depends(get_current_user)):
    items = await Item.list()
    return [ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description
    ) for item in items]

@router.post("/", response_model=ItemResponse,
            status_code=201,
            summary="Create new item",
            description="""
            Create a new item in the system.
            
            Example from `examples/basic/item_crud.py`:
            ```python
            create_item = {
                "name": "Test Item",
                "description": "A sample item for testing"
            }
            response = await client.post("/api/v1/items/", json=create_item, headers=auth_headers)
            ```
            
            **Requires**: Valid JWT token in Authorization header.
            **Note**: Description is optional and can be omitted.
            """,
            responses={
                201: {"description": "Item created successfully"},
                401: {"description": "Authentication required"},
                422: {"description": "Validation error"}
            })
async def create_item(item: ItemCreate, current_user: User = Depends(get_current_user)):
    new_item = await Item.create(
        name=item.name,
        description=item.description
    )
    return ItemResponse(
        id=new_item.id,
        name=new_item.name,
        description=new_item.description
    )

@router.get("/{item_id}", response_model=ItemResponse,
            summary="Get item by ID",
            description="""
            Retrieve a specific item by its ID.
            
            Example from `examples/basic/item_crud.py`:
            ```python
            response = await client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
            item = response.json()
            ```
            
            **Requires**: Valid JWT token in Authorization header.
            """,
            responses={
                200: {"description": "Item retrieved successfully"},
                401: {"description": "Authentication required"},
                404: {"description": "Item not found"}
            })
async def get_item(item_id: int, current_user: User = Depends(get_current_user)):
    item = await Item.read(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description
    )

@router.put("/{item_id}", response_model=ItemResponse,
            summary="Update item",
            description="""
            Update an existing item's information.
            
            Example from `examples/basic/item_crud.py`:
            ```python
            update_data = {
                "name": "Updated Test Item",
                "description": "An updated sample item"
            }
            response = await client.put(f"/api/v1/items/{item_id}", json=update_data, headers=auth_headers)
            ```
            
            **Requires**: Valid JWT token in Authorization header.
            **Note**: Provide only the fields you want to update.
            """,
            responses={
                200: {"description": "Item updated successfully"},
                400: {"description": "Empty update or validation error"},
                401: {"description": "Authentication required"},
                404: {"description": "Item not found"},
                422: {"description": "Validation error"}
            })
async def update_item(item_id: int, item_update: ItemUpdate, current_user: User = Depends(get_current_user)):
    # Filter out None values for partial updates
    update_data = {k: v for k, v in item_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    updated_item = await Item.update(item_id, **update_data)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return ItemResponse(
        id=updated_item.id,
        name=updated_item.name,
        description=updated_item.description
    )

@router.delete("/{item_id}",
             summary="Delete item",
             description="""
             Delete an item from the system.
             
             Example from `examples/basic/item_crud.py`:
             ```python
             response = await client.delete(f"/api/v1/items/{item_id}", headers=auth_headers)
             ```
             
             **Requires**: Valid JWT token in Authorization header.
             **Warning**: This action cannot be undone.
             """,
             responses={
                 200: {"description": "Item deleted successfully"},
                 401: {"description": "Authentication required"},
                 404: {"description": "Item not found"}
             })
async def delete_item(item_id: int, current_user: User = Depends(get_current_user)):
    result = await Item.delete(item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": f"Item {item_id} deleted"}
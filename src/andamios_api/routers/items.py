from fastapi import APIRouter, HTTPException
from typing import List
from andamios_api.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from andamios_api.models.item import Item

router = APIRouter()

@router.get("/", response_model=List[ItemResponse])
async def get_items():
    items = await Item.list()
    return [ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description
    ) for item in items]

@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    new_item = await Item.create(
        name=item.name,
        description=item.description
    )
    return ItemResponse(
        id=new_item.id,
        name=new_item.name,
        description=new_item.description
    )

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    item = await Item.read(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description
    )

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_update: ItemUpdate):
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

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    result = await Item.delete(item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": f"Item {item_id} deleted"}
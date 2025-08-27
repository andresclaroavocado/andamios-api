from fastapi import APIRouter, HTTPException
from typing import List
from andamios_api.schemas.item import ItemCreate, ItemResponse

router = APIRouter()

@router.get("/", response_model=List[ItemResponse])
async def get_items():
    # Example: Call andamios-orm classmethod
    # items = await ItemModel.get_all()
    # return items
    return [{"id": 1, "name": "Example Item", "description": "An example item"}]

@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    # Example: Call andamios-orm classmethod  
    # new_item = await ItemModel.create(**item.dict())
    # return new_item
    return {"id": 1, "name": item.name, "description": item.description}

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    # Example: Call andamios-orm classmethod
    # item = await ItemModel.get_by_id(item_id)
    # if not item:
    #     raise HTTPException(status_code=404, detail="Item not found")
    # return item
    return {"id": item_id, "name": "Example Item", "description": "An example item"}

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    # Example: Call andamios-orm classmethod
    # result = await ItemModel.delete_by_id(item_id)
    # if not result:
    #     raise HTTPException(status_code=404, detail="Item not found")
    return {"message": f"Item {item_id} deleted"}
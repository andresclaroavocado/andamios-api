from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ItemResponse(ItemBase):
    id: int
    
    class Config:
        from_attributes = True
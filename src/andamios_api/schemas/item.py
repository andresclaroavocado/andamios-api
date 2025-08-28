from pydantic import BaseModel, Field, validator
from typing import Optional

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Item name (required, max 200 characters)")
    description: Optional[str] = Field(None, max_length=500, description="Item description (optional, max 500 characters)")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name is required and cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None  # Convert empty string to None
        return v.strip() if v else v

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Item name (max 200 characters)")
    description: Optional[str] = Field(None, max_length=500, description="Item description (max 500 characters)")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None  # Convert empty string to None
        return v.strip() if v else v

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
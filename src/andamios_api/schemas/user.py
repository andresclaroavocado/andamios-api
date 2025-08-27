from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True
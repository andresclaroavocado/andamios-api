from fastapi import APIRouter, HTTPException
from typing import List
from andamios_api.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users():
    # Example: Call andamios-orm classmethod
    # users = await UserModel.get_all()
    # return users
    return [{"id": 1, "email": "example@example.com", "name": "Example User"}]

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # Example: Call andamios-orm classmethod  
    # new_user = await UserModel.create(**user.dict())
    # return new_user
    return {"id": 1, "email": user.email, "name": user.name}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    # Example: Call andamios-orm classmethod
    # user = await UserModel.get_by_id(user_id)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    # return user
    return {"id": user_id, "email": "example@example.com", "name": "Example User"}

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    # Example: Call andamios-orm classmethod
    # result = await UserModel.delete_by_id(user_id)
    # if not result:
    #     raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} deleted"}
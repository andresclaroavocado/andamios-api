from fastapi import APIRouter, HTTPException
from typing import List
from passlib.context import CryptContext
from andamios_api.schemas.user import UserCreate, UserUpdate, UserResponse
from andamios_api.models.user import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

@router.get("/", response_model=List[UserResponse])
async def get_users():
    users = await User.list()
    return [UserResponse(
        id=user.id,
        email=user.email, 
        name=user.name
    ) for user in users]

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    new_user = await User.create(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = await User.read(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate):
    # Filter out None values for partial updates
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    updated_user = await User.update(user_id, **update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        name=updated_user.name
    )

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    result = await User.delete(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} deleted"}
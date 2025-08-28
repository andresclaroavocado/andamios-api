from fastapi import APIRouter, HTTPException, Depends
from typing import List
from passlib.context import CryptContext
from andamios_api.schemas.user import UserCreate, UserUpdate, UserResponse
from andamios_api.models.user import User
from andamios_api.routers.auth import get_current_user

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

@router.get("/", response_model=List[UserResponse],
           summary="List all users",
           description="""
           Retrieve a list of all users in the system.
           
           Example from `examples/basic/user_crud.py`:
           ```python
           response = await client.get("/api/v1/users/", headers=auth_headers)
           users = response.json()
           ```
           
           **Requires**: Valid JWT token in Authorization header.
           """,
           responses={
               200: {"description": "List of users retrieved successfully"},
               401: {"description": "Authentication required"}
           })
async def get_users(current_user: User = Depends(get_current_user)):
    users = await User.list()
    return [UserResponse(
        id=user.id,
        email=user.email, 
        name=user.name
    ) for user in users]

@router.post("/", response_model=UserResponse,
            status_code=201,
            summary="Create new user",
            description="""
            Create a new user in the system.
            
            Example from `examples/basic/user_crud.py`:
            ```python
            create_user = {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "password": "securepassword123"
            }
            response = await client.post("/api/v1/users/", json=create_user, headers=auth_headers)
            ```
            
            **Requires**: Valid JWT token in Authorization header.
            **Note**: Password is hashed before storage and never returned in responses.
            """,
            responses={
                201: {"description": "User created successfully"},
                400: {"description": "Email already exists"},
                401: {"description": "Authentication required"},
                422: {"description": "Validation error"}
            })
async def create_user(user: UserCreate, current_user: User = Depends(get_current_user)):
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

@router.get("/{user_id}", response_model=UserResponse,
            summary="Get user by ID",
            description="""
            Retrieve a specific user by their ID.
            
            Example from `examples/basic/user_crud.py`:
            ```python
            response = await client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
            user = response.json()
            ```
            
            **Requires**: Valid JWT token in Authorization header.
            """,
            responses={
                200: {"description": "User retrieved successfully"},
                401: {"description": "Authentication required"},
                404: {"description": "User not found"}
            })
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    user = await User.read(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name
    )

@router.put("/{user_id}", response_model=UserResponse,
            summary="Update user",
            description="""
            Update an existing user's information.
            
            Example from `examples/basic/user_crud.py`:
            ```python
            update_data = {
                "name": "Alice Smith",
                "email": "alice.smith@example.com"
            }
            response = await client.put(f"/api/v1/users/{user_id}", json=update_data, headers=auth_headers)
            ```
            
            **Requires**: Valid JWT token in Authorization header.
            **Note**: Provide only the fields you want to update.
            """,
            responses={
                200: {"description": "User updated successfully"},
                400: {"description": "Empty update or validation error"},
                401: {"description": "Authentication required"},
                404: {"description": "User not found"},
                422: {"description": "Validation error"}
            })
async def update_user(user_id: int, user_update: UserUpdate, current_user: User = Depends(get_current_user)):
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

@router.delete("/{user_id}",
             summary="Delete user",
             description="""
             Delete a user from the system.
             
             Example from `examples/basic/user_crud.py`:
             ```python
             response = await client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)
             ```
             
             **Requires**: Valid JWT token in Authorization header.
             **Warning**: This action cannot be undone.
             """,
             responses={
                 200: {"description": "User deleted successfully"},
                 401: {"description": "Authentication required"},
                 404: {"description": "User not found"}
             })
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    result = await User.delete(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {user_id} deleted"}
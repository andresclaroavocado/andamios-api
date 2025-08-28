from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from andamios_api.models.user import User
from andamios_api.schemas.user import UserCreate, UserResponse
from andamios_api.core.config import settings

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    name: str = Field(..., min_length=2, max_length=50, description="User name (2-50 characters)")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=1, description="Password")

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await User.read(user_id)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse,
            summary="Register new user",
            description="""
            Create a new user account with email and password.
            
            Example from `examples/basic/auth_example.py`:
            ```python
            register_data = {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
            response = await client.post("/api/v1/auth/register", json=register_data)
            ```
            
            **Note**: Email addresses are case-insensitive and must be unique.
            """,
            responses={
                201: {"description": "User created successfully"},
                400: {"description": "Email already registered", 
                     "content": {"application/json": {"example": {
                         "detail": "Email already registered",
                         "error_code": "DUPLICATE_EMAIL",
                         "timestamp": "2023-12-07T10:00:00Z"
                     }}}},
                422: {"description": "Validation error"}
            })
async def register_user(user: UserRegister):
    # Check if email already exists
    existing_users = await User.list()
    for existing_user in existing_users:
        if existing_user.email.lower() == user.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    hashed_password = pwd_context.hash(user.password)
    try:
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
    except Exception as e:
        # Fallback in case database constraint fails
        if "UNIQUE constraint failed" in str(e) or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token,
            summary="Login user",
            description="""
            Authenticate user and return JWT access token.
            
            Example from `examples/basic/auth_example.py`:
            ```python
            login_data = {
                "email": "john@example.com",
                "password": "securepassword123"
            }
            response = await client.post("/api/v1/auth/login", json=login_data)
            token = response.json()["access_token"]
            ```
            
            Use the returned token in the Authorization header for protected endpoints:
            `Authorization: Bearer <access_token>`
            """,
            responses={
                200: {"description": "Login successful", 
                     "content": {"application/json": {"example": {
                         "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                         "token_type": "bearer"
                     }}}},
                401: {"description": "Invalid credentials",
                     "content": {"application/json": {"example": {
                         "detail": "Incorrect email or password",
                         "error_code": "LOGIN_FAILED",
                         "timestamp": "2023-12-07T10:00:00Z"
                     }}}},
                422: {"description": "Validation error"}
            })
async def login_user(user: UserLogin):
    # Get all users and find by email (simplified for this implementation)
    users = await User.list()
    db_user = None
    for u in users:
        if u.email == user.email:
            db_user = u
            break
    
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout",
            summary="Logout user", 
            description="""
            Logout current user. In the current implementation, this is primarily 
            informational as JWT tokens are stateless.
            
            Example from `examples/basic/auth_example.py`:
            ```python
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.post("/api/v1/auth/logout", headers=headers)
            ```
            
            **Note**: For production use, implement token blacklisting for enhanced security.
            """,
            responses={
                200: {"description": "Logout successful"},
                401: {"description": "Authentication required"}
            })
async def logout_user(current_user: User = Depends(get_current_user)):
    # In a real implementation, you would blacklist the token
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse,
           summary="Get current user profile",
           description="""
           Get the profile of the currently authenticated user.
           
           Example from `examples/basic/auth_example.py`:
           ```python
           headers = {"Authorization": f"Bearer {access_token}"}
           response = await client.get("/api/v1/auth/me", headers=headers)
           profile = response.json()
           ```
           
           **Requires**: Valid JWT token in Authorization header.
           """,
           responses={
               200: {"description": "User profile retrieved successfully"},
               401: {"description": "Authentication required or token invalid"}
           })
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name
    )
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from andamios_orm import initialize_database
from andamios_api.routers import users, items, auth
from andamios_api.core.config import settings
from andamios_api.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

# Import models to register them with SQLAlchemy metadata
from andamios_api.models.user import User
from andamios_api.models.item import Item

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and create tables
    # Models are imported above, so their metadata is registered
    await initialize_database(create_tables=False, drop_existing=False)
    
    # Manually create tables for our API models only
    from andamios_orm import get_engine
    from andamios_api.models.user import APIBase
    
    engine = get_engine()
    
    # Use sync method to create tables for our API models only
    def create_api_tables():
        APIBase.metadata.create_all(engine)
    
    import asyncio
    await asyncio.to_thread(create_api_tables)
    
    yield
    # Shutdown: cleanup if needed
    pass

app = FastAPI(
    title="Andamios API",
    description="""
    Async HTTP API that reuses andamios-orm for database operations.
    
    ## Features
    
    - **User Management**: Create, read, update, and delete users
    - **Item Management**: Complete CRUD operations for items
    - **Authentication**: JWT-based authentication system
    - **Input Validation**: Comprehensive validation with detailed error messages
    - **Environment Configuration**: Support for development, test, and production environments
    
    ## Getting Started
    
    1. **Register a user**: `POST /api/v1/auth/register`
    2. **Login**: `POST /api/v1/auth/login` to get JWT token
    3. **Use authenticated endpoints**: Add `Authorization: Bearer <token>` header
    
    ## Examples
    
    Complete runnable examples are available in the `examples/` directory:
    
    - `user_crud.py` - User management operations
    - `item_crud.py` - Item management operations  
    - `auth_example.py` - Authentication flow
    - `validation_example.py` - Input validation examples
    - `error_handling_example.py` - Error handling examples
    - `config_example.py` - Configuration examples
    
    Run all examples: `python examples/run_examples.py`
    
    ## Authentication
    
    Most endpoints require JWT authentication. Get a token by registering and logging in:
    
    ```python
    # Register
    response = await client.post("/api/v1/auth/register", json={
        "name": "John Doe",
        "email": "john@example.com", 
        "password": "securepassword123"
    })
    
    # Login
    response = await client.post("/api/v1/auth/login", json={
        "email": "john@example.com",
        "password": "securepassword123"
    })
    token = response.json()["access_token"]
    
    # Use token
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/users/", headers=headers)
    ```
    """,
    version="0.1.0",
    debug=settings.api_debug,
    lifespan=lifespan,
    contact={
        "name": "Andamios API",
        "url": "https://github.com/andresclaroavocado/andamios-api",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_methods_list,
    allow_headers=[settings.cors_allow_headers] if settings.cors_allow_headers != "*" else ["*"]
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])

@app.get("/")
async def root():
    return {"message": "Andamios API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
from fastapi import FastAPI
from contextlib import asynccontextmanager
from andamios_orm import initialize_database
from andamios_api.routers import users, items
from andamios_api.core.config import settings

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
    description="Async HTTP API that reuses andamios-orm for database operations",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])

@app.get("/")
async def root():
    return {"message": "Andamios API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
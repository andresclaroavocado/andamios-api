from fastapi import FastAPI
from andamios_api.routers import users, items
from andamios_api.core.config import settings

app = FastAPI(
    title="Andamios API",
    description="Async HTTP API that reuses andamios-orm for database operations",
    version="0.1.0"
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
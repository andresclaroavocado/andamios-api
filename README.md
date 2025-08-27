# Andamios API

An async HTTP API built with FastAPI that reuses andamios-orm for database operations.

## Overview

Andamios API is designed as a lightweight API layer that delegates all database operations to andamios-orm classmethods. The API layer focuses solely on HTTP request/response handling, validation, and authentication, while andamios-orm handles all database/engine/model management.

## Features

- **Async FastAPI**: High-performance async HTTP API
- **andamios-orm Integration**: Delegates all database operations to andamios-orm classmethods
- **Clean Architecture**: API layer doesn't manage DB/engines/models directly
- **OpenAPI Documentation**: Auto-generated interactive API documentation
- **Type Safety**: Full Pydantic schema validation

## Project Structure

```
andamios-api/
├── src/
│   └── andamios_api/   # Main package
│       ├── core/       # Core configuration and utilities
│       ├── models/     # Pydantic models (not DB models)
│       ├── routers/    # FastAPI route handlers
│       ├── schemas/    # Request/response schemas
│       └── utils/      # Utility functions
├── examples/           # Usage examples
├── tests/             # Test suite
└── docs/              # Additional documentation
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/andresclaroavocado/andamios-api.git
cd andamios-api

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running the API

```bash
# Start the development server
uvicorn src.andamios_api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Example Usage

```python
import asyncio
import httpx

async def example():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Health check
        response = await client.get("/health")
        print(response.json())
        
        # Create a user
        user_data = {
            "email": "user@example.com",
            "name": "Test User",
            "password": "secret123"
        }
        response = await client.post("/api/v1/users/", json=user_data)
        print("Created user:", response.json())

asyncio.run(example())
```

## API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check

### Users
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `DELETE /api/v1/users/{user_id}` - Delete user

### Items
- `GET /api/v1/items/` - List all items
- `POST /api/v1/items/` - Create a new item
- `GET /api/v1/items/{item_id}` - Get item by ID
- `DELETE /api/v1/items/{item_id}` - Delete item

## Architecture Principles

1. **Separation of Concerns**: API layer handles HTTP concerns only
2. **Delegation Pattern**: All database operations delegated to andamios-orm
3. **No Direct DB Access**: API never manages connections, engines, or models directly
4. **Schema Validation**: All inputs/outputs validated with Pydantic
5. **Async First**: Built for high-performance async operations

## Development Status

This project is in early development. Current implementation includes:
- ✅ Basic project structure
- ✅ Example API endpoints (with placeholder implementations)
- ✅ Pydantic schemas for validation
- ✅ FastAPI application setup
- ❌ andamios-orm integration (see issues)
- ❌ Authentication system
- ❌ Comprehensive error handling
- ❌ Test suite
- ❌ Production configuration

## Contributing

See the [Issues](https://github.com/andresclaroavocado/andamios-api/issues) for planned development tasks:

1. [Integrate andamios-orm models](https://github.com/andresclaroavocado/andamios-api/issues/1)
2. [Add authentication and authorization middleware](https://github.com/andresclaroavocado/andamios-api/issues/2)
3. [Add comprehensive error handling and validation](https://github.com/andresclaroavocado/andamios-api/issues/3)
4. [Add comprehensive test suite](https://github.com/andresclaroavocado/andamios-api/issues/4)
5. [Add API documentation and OpenAPI spec](https://github.com/andresclaroavocado/andamios-api/issues/5)
6. [Add configuration management and environment setup](https://github.com/andresclaroavocado/andamios-api/issues/6)

## License

MIT License
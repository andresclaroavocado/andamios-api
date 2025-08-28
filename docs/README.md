# Andamios API Documentation

Async HTTP API that reuses andamios-orm for database operations.

## Quick Start

### 1. Start the API Server

```bash
# Development
uvicorn src.andamios_api.main:app --port 8001 --reload

# Production  
ENVIRONMENT=production uvicorn src.andamios_api.main:app --host 0.0.0.0 --port 8000
```

### 2. View Interactive Documentation

- **OpenAPI/Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

### 3. Run Examples

All examples are fully runnable and demonstrate real API usage:

```bash
# Run all examples
python examples/run_examples.py

# Run individual examples
python examples/basic/user_crud.py
python examples/basic/item_crud.py
python examples/basic/auth_example.py
python examples/basic/validation_example.py
python examples/basic/error_handling_example.py
python examples/basic/config_example.py
```

## API Overview

### Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register**: `POST /api/v1/auth/register`
2. **Login**: `POST /api/v1/auth/login` - Returns JWT token
3. **Use Token**: Add `Authorization: Bearer <token>` header to requests

### Core Resources

#### Users (`/api/v1/users/`)
- `GET /` - List all users
- `POST /` - Create user
- `GET /{user_id}` - Get user by ID
- `PUT /{user_id}` - Update user  
- `DELETE /{user_id}` - Delete user

#### Items (`/api/v1/items/`)
- `GET /` - List all items
- `POST /` - Create item
- `GET /{item_id}` - Get item by ID
- `PUT /{item_id}` - Update item
- `DELETE /{item_id}` - Delete item

#### Authentication (`/api/v1/auth/`)
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token
- `GET /me` - Get current user profile
- `POST /logout` - Logout (informational)

### Error Handling

All API errors follow a consistent structure:

```json
{
  "detail": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2023-12-07T10:00:00Z",
  "validation_errors": [...]  // Only for 422 validation errors
}
```

Common error codes:
- `USER_NOT_FOUND` - User doesn't exist
- `ITEM_NOT_FOUND` - Item doesn't exist  
- `DUPLICATE_EMAIL` - Email already registered
- `AUTHENTICATION_FAILED` - Invalid or missing token
- `LOGIN_FAILED` - Invalid credentials
- `VALIDATION_ERROR` - Input validation failed
- `EMPTY_UPDATE` - No fields provided for update

## Environment Configuration

The API supports multiple environments with automatic configuration:

### Environment Files

- `.env.development` - Local development (default)
- `.env.test` - Test environment  
- `.env.production` - Production settings

### Environment Variables

Set `ENVIRONMENT=production` to use production configuration.

Key settings:
- `DATABASE_URL` - Database connection string
- `JWT_SECRET_KEY` - JWT signing secret
- `API_HOST`, `API_PORT` - Server binding
- `CORS_ALLOW_ORIGINS` - CORS allowed origins

## Examples Reference

### Authentication Flow

```python
import httpx

async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
    # Register
    register_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword123"
    }
    response = await client.post("/api/v1/auth/register", json=register_data)
    
    # Login
    login_data = {
        "email": "john@example.com",
        "password": "securepassword123"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    # Use token for authenticated requests
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/users/", headers=headers)
```

### CRUD Operations

```python
# Create
create_data = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
response = await client.post("/api/v1/users/", json=create_data, headers=headers)
user = response.json()

# Read
response = await client.get(f"/api/v1/users/{user['id']}", headers=headers)
user = response.json()

# Update
update_data = {"name": "Alice Smith"}
response = await client.put(f"/api/v1/users/{user['id']}", json=update_data, headers=headers)

# Delete
response = await client.delete(f"/api/v1/users/{user['id']}", headers=headers)
```

### Input Validation

All endpoints include comprehensive input validation:

- **Email fields**: Must be valid email format
- **Name fields**: 2-50 characters, trimmed of whitespace
- **Password fields**: Minimum 8 characters  
- **Required fields**: Clear error messages for missing fields
- **Empty updates**: Rejected with specific error code

### Error Handling

Examples demonstrate proper error handling patterns:

```python
try:
    response = await client.get("/api/v1/users/99999", headers=headers)
    response.raise_for_status()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        error = e.response.json()
        print(f"Not found: {error['error_code']}")
    elif e.response.status_code == 422:
        error = e.response.json() 
        for val_error in error.get('validation_errors', []):
            print(f"Validation: {val_error['field']} - {val_error['message']}")
```

## Testing

### Run Tests

```bash
# All tests
pytest

# Unit tests only  
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=src/andamios_api --cov-report=html
```

### Test Structure

- **Unit tests** (`tests/unit/`) - Schema validation, business logic
- **Integration tests** (`tests/integration/`) - Full API testing with real HTTP calls
- **Test fixtures** - Automatic test server startup and authentication

Integration tests mirror the examples exactly, ensuring examples work correctly.

## Development

### Example-Driven Development

This project follows Example-Driven Development (EDD):

1. **Examples first** - All features start as runnable examples
2. **Real usage** - Examples show actual client usage patterns  
3. **Test mirrors** - Integration tests mirror examples exactly
4. **Documentation source** - Examples become API documentation

### Project Structure

```
andamios-api/
├── src/andamios_api/           # Main API code
│   ├── core/                   # Configuration and exceptions
│   ├── models/                 # Database models (andamios-orm)
│   ├── routers/               # FastAPI route handlers
│   └── schemas/               # Pydantic validation schemas
├── examples/                   # Runnable examples
│   └── basic/                 # Basic CRUD examples
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
└── docs/                      # Documentation
```

### Adding New Features

1. Create working example in `examples/basic/`
2. Add integration test that mirrors the example
3. Implement API endpoint with proper documentation
4. Update OpenAPI documentation with example references
5. Verify example works with `python examples/run_examples.py`

This ensures all features are example-driven and actually work as documented.
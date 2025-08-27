# Andamios API Examples - Ultra-Simple EDD

Ultra-simple Example-Driven Development (EDD) examples. Each example demonstrates complete CRUD operations using HTTP API endpoints, following the narrative: **start API → HTTP client → CREATE → READ → UPDATE → DELETE**.

## Examples Structure

**1 comprehensive example per resource × 2 resources = 2 total examples**

### Complete CRUD Examples
- **`user_crud.py`** - User: Complete CREATE → READ → UPDATE → DELETE operations
- **`item_crud.py`** - Item: Complete CREATE → READ → UPDATE → DELETE operations

## Running Examples

```bash
# First, start the API server
uvicorn src.andamios_api.main:app --reload

# Then run any specific example
python examples/basic/user_crud.py
python examples/basic/item_crud.py

# Run all examples
python examples/run_examples.py
```

## Example Pattern

Each example follows this comprehensive CRUD pattern:

```python
"""
[Resource] CRUD Example

Complete Create, Read, Update, Delete operations for [Resource] API endpoints.
Narrative: HTTP client → POST create → GET read → PUT update → DELETE
"""

import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # CREATE: POST /api/v1/[resource]/
        # READ: GET /api/v1/[resource]/ and GET /api/v1/[resource]/{id}
        # UPDATE: PUT /api/v1/[resource]/{id} (when implemented)
        # DELETE: DELETE /api/v1/[resource]/{id}
        pass

if __name__ == "__main__":
    asyncio.run(main())
```

## EDD Principles

- **Comprehensive**: All CRUD operations in one example
- **No API Definitions**: Uses existing API endpoints only
- **Clear Narrative**: Each example follows complete HTTP story
- **Real HTTP**: No mocks, actual API calls
- **Async + httpx**: Modern async HTTP patterns
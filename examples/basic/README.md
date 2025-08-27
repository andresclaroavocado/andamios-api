# Basic CRUD Examples

Ultra-simple API CRUD examples following andamios-orm discipline.

## Examples

- **`user_crud.py`** - Complete User CRUD operations
- **`item_crud.py`** - Complete Item CRUD operations

## Rules

Each example follows strict discipline:
- **No server setup** - Uses running API server only
- **No schema definitions** - Uses existing API contracts
- **Client-only** - Pure HTTP client operations
- **Complete CRUD** - CREATE → READ → UPDATE → DELETE in one file

## Usage

```bash
# Start API server first
uvicorn src.andamios_api.main:app --reload

# Run individual examples  
python user_crud.py
python item_crud.py
```
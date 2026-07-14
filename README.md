# FastAPI Extended Query Method

Native HTTP QUERY support for FastAPI.

## Overview

`FastAPIWithQueryHttpMethod` extends FastAPI with native support for the
HTTP QUERY method while preserving the FastAPI developer experience.

## Installation

``` bash
pip install fastapi-extended-query-method
```

## Quick Start

``` python
import uuid
from typing import List, Optional
import uvicorn
from fastapi import Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 1. Initialize the app using your custom class
from fastapi_extended_query_method import FastAPIWithQueryHttpMethod

app = FastAPIWithQueryHttpMethod(query_saving_cache=True)

# 2. Mock Data for quick testing
MOCK_PRODUCTS = [
    {"id": 1, "name": "Gaming Laptop", "category": "electronics", "price": 1200.99},
    {"id": 2, "name": "Smartphone", "category": "electronics", "price": 599.99},
    {"id": 3, "name": "Bluetooth Headphones", "category": "electronics", "price": 79.90},
    {"id": 4, "name": "Espresso Machine", "category": "appliances", "price": 150.00},
    {"id": 5, "name": "Blender", "category": "appliances", "price": 45.50},
    {"id": 6, "name": "Office Chair", "category": "furniture", "price": 180.00},
]

# 3. Pydantic Schemas
class SearchFilters(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class ProductSchema(BaseModel):
    id: int
    name: str
    category: str
    price: float

class SearchResponse(BaseModel):
    status: str
    execution_id: str
    total_found: int
    products: List[ProductSchema]


# 4. Filter function simulating database queries with mock data
def get_products_from_sqlite(filters: SearchFilters, limit: int, order_by: str):
    results = MOCK_PRODUCTS.copy()
    
    # Apply search filters if they are provided
    if filters.category:
        results = [p for p in results if p["category"].lower() == filters.category.lower()]
        
    if filters.min_price is not None:
        results = [p for p in results if p["price"] >= filters.min_price]
        
    if filters.max_price is not None:
        results = [p for p in results if p["price"] <= filters.max_price]
    
    # Sort results dynamically (defaults to "id")
    results = sorted(results, key=lambda x: x.get(order_by, x["id"]))
    
    # Apply limit
    return results[:limit]


# 5. Endpoint using your custom @app.query decorator
@app.query("/products/filter", response_model=SearchResponse)
async def filter_products(
    filters: SearchFilters,
    limit: int = Query(default=10, ge=1),
    order_by: str = "id",
):
    # Fetch and filter the mock data
    filtered_products = get_products_from_sqlite(
        filters=filters,
        limit=limit,
        order_by=order_by,
    )

    execution_id = str(uuid.uuid4())

    return JSONResponse(
        content={
            "status": "success",
            "execution_id": execution_id,
            "total_found": len(filtered_products),
            "products": filtered_products,
        },
        headers={
            "X-Execution-Id": execution_id,
        },
    )


# 6. Direct startup block
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
```

## Swagger compatibility

After starting the application:

    http://localhost:8000/docs

OpenAPI and Swagger do **not** currently support the HTTP QUERY method.

For that reason this package automatically exposes QUERY endpoints as
both:

-   QUERY
-   POST

Use the **POST** operation in Swagger only for interactive testing.

Real clients should invoke the QUERY method directly.

<p align="center">
  <img src="https://raw.githubusercontent.com/JorgeCardona/fastapi-extended-query-method/refs/heads/main/images/swagger.png" alt="Swagger Interface" width="900">
</p>

## Cache

`query_saving_cache=True` allows caching.

`query_saving_cache=False` automatically adds:

-   Cache-Control: no-store
-   Pragma: no-cache
-   Expires: 0

## Testing API

``` bash
python validate_data/test_api_query_method.py
```

<p align="center">
  <img src="https://raw.githubusercontent.com/JorgeCardona/fastapi-extended-query-method/refs/heads/main/images/api_results.png" alt="API Results" width="900">
</p>

## Testing Cache

### Using Cache Stored
``` bash
python validate_data/test_cache_comparison.py
```
<p align="center">
  <img src="https://raw.githubusercontent.com/JorgeCardona/fastapi-extended-query-method/refs/heads/main/images/cache.png" alt="Stored Cache" width="900">
</p>

### NO Using Cache Stored
<p align="center">
  <img src="https://raw.githubusercontent.com/JorgeCardona/fastapi-extended-query-method/refs/heads/main/images/no_cache.png" alt="Without Cache" width="900">
</p>

## License

MIT

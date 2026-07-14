import os
import uuid

from fastapi.responses import JSONResponse

from fastapi import Query

from src.fastapi_extended_query_method import FastAPIWithQueryHttpMethod
from validate_data.utils.models import SearchFilters, SearchResponse
from validate_data.utils.db_example_config import get_products_from_sqlite

app = FastAPIWithQueryHttpMethod(
    query_saving_cache=os.getenv("QUERY_SAVING_CACHE", "true").lower() == "true"
)


@app.query("/products/filter", response_model=SearchResponse)
async def filter_products(
    filters: SearchFilters,
    limit: int = Query(default=10, ge=1),
    order_by: str = "id",
):
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


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "query_saving_cache": app.query_saving_cache,
    }
from pydantic import BaseModel

# ---- [ES] MODELOS DE PYDANTIC (ENTRADA Y SALIDA) ----
# ---- [EN] PYDANTIC MODELS (INPUT AND OUTPUT) ----

class SearchFilters(BaseModel):
    """
    [ES] Modelo de entrada para los filtros de búsqueda de productos.
    [EN] Input model for product search filters.
    """
    categories: list[str]
    max_price: float
    excluded_brands: list[str]


class ProductFormat(BaseModel):
    """
    [ES] Modelo que define la estructura estándar de un producto.
    [EN] Model defining the standard structure of a product.
    """
    id: int
    name: str
    category: str
    price: float
    brand: str


class SearchResponse(BaseModel):
    """
    [ES] Modelo de salida para la respuesta de la búsqueda.
    [EN] Output model for the search response.
    """
    status: str
    total_found: int
    products: list[ProductFormat]
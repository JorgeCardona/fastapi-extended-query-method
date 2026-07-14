from typing import Any, Callable
from fastapi import FastAPI, Request, Response
from fastapi.openapi.utils import get_openapi
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)

class FastAPIWithQueryHttpMethod(FastAPI):
    """
    [ES] Clase FastAPI modificada que habilita soporte nativo y visual para el método HTTP QUERY
         y permite configurar automáticamente el guardado de caché para dicho método.

    [EN] Modified FastAPI class that enables native and visual support for the HTTP QUERY method
         and allows configuring cache saving for this method.
    """

    def __init__(
        self,
        *args: Any,
        query_saving_cache: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.query_saving_cache = query_saving_cache

        @self.middleware("http")
        async def add_query_cache_headers(
            request: Request,
            call_next: Callable[[Request], Any],
        ) -> Response:
            response: Response = await call_next(request)

            # [ES] Cuando el modo de guardado de caché está deshabilitado para QUERY,
            #      evitamos que clientes, proxies o navegadores almacenen en caché
            #      la respuesta, ya que este método puede transportar información
            #      sensible.
            #
            # [EN] When cache saving mode is disabled for QUERY,
            #      prevent clients, proxies and browsers from caching the response,
            #      since this method may carry sensitive information.
            if not self.query_saving_cache and request.method.upper() == "QUERY":
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
                logger.info("QUERY cache saving is disabled. Clients, browsers, and proxies will not cache responses containing sensitive data.")

            return response

    def query(self, path: str, **kwargs: Any):
        """
        [ES] Decorador para registrar un endpoint que acepte tanto POST como QUERY.
             Se usa POST para que Swagger UI no lo rompa y permita probarlo desde la web,
             y QUERY para soportar peticiones con dicho método HTTP real.

        [EN] Decorator to register an endpoint that accepts both POST and QUERY.
             POST is used so Swagger UI doesn't break and allows testing it from the web,
             and QUERY to support requests with that actual HTTP method.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Ruta visible en Swagger (POST)
            self.add_api_route(
                path,
                func,
                methods=["POST"],
                **kwargs,
            )

            # Ruta real para QUERY (oculta del esquema OpenAPI)
            query_kwargs = dict(kwargs)
            query_kwargs.pop("response_model", None)
            query_kwargs["include_in_schema"] = False

            self.add_api_route(
                path,
                func,
                methods=["QUERY"],
                **query_kwargs,
            )

            return func

        return decorator

    def openapi(self) -> dict[str, Any]:
        """
        [ES] Genera el esquema OpenAPI estándar garantizando que la ruta sea visible.

        [EN] Generates the standard OpenAPI schema ensuring that the route is visible.
        """
        if self.openapi_schema:
            return self.openapi_schema

        openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            openapi_version=self.openapi_version,
            description=self.description,
            routes=self.routes,
        )

        self.openapi_schema = openapi_schema
        return self.openapi_schema

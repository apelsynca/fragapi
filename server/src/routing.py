from src.kit.routing import IncludedInSchemaAPIRoute, get_api_router_class


class APIRoute(IncludedInSchemaAPIRoute):
    pass


APIRouter = get_api_router_class(APIRoute)

__all__ = ["APIRouter"]

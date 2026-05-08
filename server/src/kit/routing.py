from collections.abc import Callable
from typing import Any

from fastapi import APIRouter as _APIRouter
from fastapi.routing import APIRoute

from src.config import settings
from src.openapi import APITag


class IncludedInSchemaAPIRoute(APIRoute):
    """
    A subclass of `APIRoute` that automatically sets the `include_in_schema` property
    depending on the tags.
    """

    def __init__(self, path: str, endpoint: Callable[..., Any], **kwargs: Any) -> None:
        super().__init__(path, endpoint, **kwargs)
        tags = self.tags
        if self.include_in_schema:
            if APITag.private in tags:
                self.include_in_schema = settings.is_development()
            elif APITag.public in tags:
                self.include_in_schema = True
            else:
                self.include_in_schema = False


def _inherit_signature_from[**P, T](
    _: Callable[P, T],
) -> Callable[[Callable[..., T]], Callable[P, T]]:
    return lambda x: x  # pyright: ignore


def get_api_router_class(route_class: type[APIRoute]) -> type[_APIRouter]:
    """
    Returns a subclass of `APIRouter` that uses the given `route_class`.
    """

    class _CustomAPIRouter(_APIRouter):
        @_inherit_signature_from(_APIRouter.__init__)
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs["route_class"] = route_class
            super().__init__(*args, **kwargs)

    return _CustomAPIRouter

from enum import StrEnum
from typing import Any, NotRequired, TypedDict

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field

from src.config import settings


class OpenAPITag(TypedDict):
    name: str
    description: NotRequired[str]
    externalDocs: NotRequired[dict[str, str]]


class APITag(StrEnum):
    """
    Tags used by our documentation to better organize the endpoints.

    They should be set after the "group" tag, which is used to group the endpoints
    in the generated documentation.

    **Example**

        ```py
        router = APIRouter(prefix="/products", tags=["products", APITag.public])
        ```
    """

    private = "private"
    public = "public"

    @classmethod
    def metadata(cls) -> list[OpenAPITag]:
        return [
            {
                "name": cls.private,
                "description": (
                    "Endpoints that should appear in the schema only "
                    "in development to generate our internal panel."
                ),
            },
            {
                "name": cls.public,
                "description": (
                    "Endpoints shown and documented in the FragAPI documentation."
                ),
            },
        ]


class ErrorResponse(BaseModel):
    error: str = Field(description="Error name", examples=["BadRequest"])
    detail: str = Field(description="What went wrong")


_ERROR_RESPONSES: dict[int, dict[str, Any]] = {
    400: {
        "model": ErrorResponse,
        "description": "The request can't be done, for example insufficient funds",
    },
    401: {
        "model": ErrorResponse,
        "description": "Missing or invalid token, or it lacks the required scope",
    },
    404: {"model": ErrorResponse, "description": "Not found"},
    # Sent by the rate limit middleware, without a JSON body.
    429: {"description": "Too many requests, retry later"},
}


def error_responses(*status_codes: int) -> dict[int | str, dict[str, Any]]:
    """Error responses to document on a router or a route."""
    return {code: _ERROR_RESPONSES[code] for code in status_codes}


class OpenAPIParameters(TypedDict):
    title: str
    summary: str
    version: str
    description: str
    openapi_tags: list[dict[str, Any]]
    servers: list[dict[str, Any]] | None


OPENAPI_PARAMETERS: OpenAPIParameters = {
    "title": "FragAPI",
    "summary": "API to interact with fragment.com",
    "version": "1.0.0",
    "description": "Read the docs at https://docs.fragapi.com",
    "openapi_tags": APITag.metadata(),  # type: ignore
    "servers": None
    if settings.is_development()
    else [
        {
            "url": "https://api.fragapi.com",
            "description": "Production environment",
        },
        {
            "url": "https://sandbox-api.fragapi.com",
            "description": "Sandbox environment",
        },
    ],
}


def set_openapi_generator(app: FastAPI) -> None:
    def _openapi_generator() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            summary=app.summary,
            description=app.description,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            webhooks=app.webhooks.routes,
            tags=app.openapi_tags,
            servers=app.servers,
            separate_input_output_schemas=app.separate_input_output_schemas,
        )

        return openapi_schema

    app.openapi = _openapi_generator  # type: ignore[method-assign]


__all__ = [
    "OPENAPI_PARAMETERS",
    "APITag",
    "ErrorResponse",
    "error_responses",
    "set_openapi_generator",
]

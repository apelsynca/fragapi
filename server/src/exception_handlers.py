from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions import AppError, BadRequest, ResourceNotFound, Unauthorized


async def app_exception_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": type(exc).__name__, "detail": exc.message},
    )


async def unauthorized_exception_handler(_: Request, exc: Unauthorized) -> JSONResponse:
    return JSONResponse(
        status_code=401, content={"error": type(exc).__name__, "detail": exc.message}
    )


async def resource_not_found_exc_handler(
    _: Request, exc: ResourceNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=404, content={"error": type(exc).__name__, "detail": exc.message}
    )


async def bad_request_exc_handler(_: Request, exc: BadRequest) -> JSONResponse:
    return JSONResponse(
        status_code=400, content={"error": type(exc).__name__, "detail": exc.message}
    )


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        AppError,
        app_exception_handler,  # type: ignore
    )

    app.add_exception_handler(
        Unauthorized,
        unauthorized_exception_handler,  # type: ignore
    )

    app.add_exception_handler(
        ResourceNotFound,
        resource_not_found_exc_handler,  # type: ignore
    )

    app.add_exception_handler(
        BadRequest,
        bad_request_exc_handler,  # type: ignore
    )

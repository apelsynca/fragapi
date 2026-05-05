from collections.abc import Sequence
from typing import Any, LiteralString, NotRequired, TypedDict

from pydantic_core import ErrorDetails, InitErrorDetails, PydanticCustomError
from pydantic_core import ValidationError as PydanticValidationError


class FragError(Exception):
    def __init__(self, message: str = "Frag error", status_code: int = 500):
        super().__init__(message)

        self.message = message
        self.status_code = status_code


class BadRequest(FragError):
    def __init__(self, message: str = "Bad request", status_code: int = 400):
        super().__init__(message=message, status_code=status_code)


class ResourceNotFound(BadRequest):
    def __init__(self, message: str = "Not found"):
        super().__init__(message=message, status_code=404)


class Unauthorized(BadRequest):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401)


class Forbidden(BadRequest):
    def __init__(self, message: str = "No rights"):
        super().__init__(message=message, status_code=403)


class InsuficcientFunds(BadRequest):
    def __init__(self, message: str = "Insuficcient funds", status_code: int = 400):
        super().__init__(message, status_code)


class ValidationError(TypedDict):
    loc: tuple[int | str, ...]
    msg: LiteralString
    type: LiteralString
    input: Any
    ctx: NotRequired[dict[str, Any]]
    url: NotRequired[str]


class FragRequestValidationError(FragError):
    def __init__(self, errors: Sequence[ValidationError]) -> None:
        self._errors = errors

    def errors(self) -> list[ErrorDetails]:
        pydantic_errors: list[InitErrorDetails] = []
        for error in self._errors:
            pydantic_errors.append(
                {
                    "type": PydanticCustomError(error["type"], error["msg"]),
                    "loc": error["loc"],
                    "input": error["input"],
                }
            )
        pydantic_error = PydanticValidationError.from_exception_data(
            self.__class__.__name__, pydantic_errors
        )
        return pydantic_error.errors()

class AppError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

        self.message = message


class BadRequest(AppError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message)


class ResourceNotFound(AppError):
    def __init__(self, message: str = "Not found"):
        super().__init__(message)


class Unauthorized(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message)


class NotPermitted(AppError):
    def __init__(self, message: str = "No rights"):
        super().__init__(message)


class InsuficcientFunds(BadRequest):
    def __init__(self, message: str = "Insufficient Funds"):
        super().__init__(message)

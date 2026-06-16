from src.exceptions import Unauthorized


class InsufficientScopeError(Unauthorized):
    def __init__(self, message: str = "Insufficient scope"):
        super().__init__(message)

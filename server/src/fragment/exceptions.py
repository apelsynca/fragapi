class FragmentError(Exception):
    """On any unexpected fragment response/request"""

    def __init__(self, message: str = "Fragment error") -> None:
        self.message = message
        super().__init__(message)


class FragmentBadRequest(FragmentError):
    """When error field exists in fragment request"""

    pass

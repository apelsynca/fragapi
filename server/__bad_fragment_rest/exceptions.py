class FragmentRestError(Exception):
    """On any unexpected fragment response/request"""

    def __init__(self, message: str = "Fragment error") -> None:
        self.message = message
        super().__init__(message)


class FragmentBadRequest(FragmentRestError):
    """When error field exists in fragment request"""

    pass


class FragmentUserNotFound(FragmentRestError):
    pass

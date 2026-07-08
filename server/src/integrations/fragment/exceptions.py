class FragmentError(Exception):
    pass


class FragmentAPIError(Exception):
    """
    General API error class.
    """

    # NOTE: there might be an error code aswell, which could be usefull
    # NOTE: message is optional now, rethink
    def __init__(self, message: str | None = None) -> None:
        self.message = message
        super().__init__(message)


class FragmentAPIUsersNotFound(FragmentAPIError):
    """
    When user is not found.
    """

    pass


class FragmentAPINotAUser(FragmentAPIError):
    """
    When channel/group is found, instead of the user.
    """

    pass


class FragmentAPIAccessDenied(FragmentAPIError):
    """
    When session is somehow dead, should not happen.
    """

    pass

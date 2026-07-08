class FragmentError(Exception):
    pass


class FragmentAPIError(Exception):
    """
    General API error class.
    """

    pass


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

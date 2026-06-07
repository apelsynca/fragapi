class FragmentError(Exception):
    pass


class FragmentAPIError(Exception):
    pass


class FragmentAPIUsersNotFound(FragmentAPIError):
    pass


class FragmentAPIAccessDenied(FragmentAPIError):
    pass

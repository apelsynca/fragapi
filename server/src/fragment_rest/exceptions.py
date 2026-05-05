class FragmentAPIError(Exception):
    pass


class FragmentAPIBadRequest(Exception):
    pass


class FragmentAPIUsersNotFound(FragmentAPIBadRequest):
    pass


class FragmentAPIAccessDenied(FragmentAPIBadRequest):
    pass


class FragmentAuthError(Exception):
    pass

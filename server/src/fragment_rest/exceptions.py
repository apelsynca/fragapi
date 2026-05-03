class FragmentAPIError(Exception):
    pass


class FragmentAPIBadRequest(Exception):
    pass


class FragmentAPINotAuthorized(Exception):
    pass


class FragmentAPIUsersNotFound(FragmentAPIBadRequest):
    pass


# --- diff?


class FragmentAuthError(Exception):
    pass

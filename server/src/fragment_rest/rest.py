from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.fragment_rest.models import FragmentSession
from src.kit.ton_connect import TonConnect


class FragmentRest:
    def __init__(self, ton_connect: TonConnect) -> None:
        self._api = FragmentAPIClient(ton_connect=ton_connect)
        self._auth = FragmentRestAuth(ton_connect=ton_connect)
        self._session: FragmentSession | None = None

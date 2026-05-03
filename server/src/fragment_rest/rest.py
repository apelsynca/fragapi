from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.kit.ton_connect import TonConnect


class FragmentRest:
    def __init__(self, ton_connect: TonConnect) -> None:
        self._api = FragmentAPIClient(ton_connect=ton_connect)
        self._auth = FragmentRestAuth(api_client=self._api, ton_connect=ton_connect)

import json
import re
from asyncio import sleep

from httpx import AsyncClient
from tonutils.contracts import WalletV5R1

from src.config import settings
from src.kit.ton_connect import TonConnect
from src.logging import get_logger

from .exceptions import FragmentBadRequest, FragmentError
from .types import FragmentSession

log = get_logger()


class BaseFragmentRest:
    """
    Base class for Fragment, containing:
        - Authorization
        - Session persistance
        - HTTPX Client
        - method named `request` to simplify requests to fragment
    """

    def __init__(
        self, wallet: WalletV5R1, base_url: str = "https://fragment.com"
    ) -> None:
        self.base_url = base_url

        self._client: AsyncClient | None = None
        self._authorized = False
        self._ton_rate: float | None = None

        self._session = self.load_session()
        self.tc = TonConnect(wallet, "")

    async def authorize(self) -> None:
        if self._authorized:
            return

        is_authorized = await self.check_auth()
        if is_authorized:
            log.info("Was already authorized to fragment")
            self._authorized = True
            return

        await self.get_session_tokens()  # get initial session tokens
        if self._session.ton_proof is None:
            raise FragmentError("Ton Proof is None")
        await sleep(0.1)

        authorized = await self.check_auth()
        log.info("Authorized to fragment!", authorized=authorized)

        await sleep(0.2)
        await self.get_session_tokens()  # get authorized session tokens

        self.save_session()
        self._authorized = True

    async def check_auth(self) -> bool:
        if self._session.ton_proof is None or self._session.hash is None:
            return False

        data = self.tc.get_connect_request_data(
            ton_proof_payload=self._session.ton_proof
        )
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
        }

        try:
            auth_data = await self.request(
                method="checkTonProofAuth", data=data, headers=headers, authorize=False
            )
        except FragmentBadRequest:
            return False

        if auth_data.get("verified", False):
            return True
        return False

    async def get_session_tokens(self) -> None:
        response = await self.client.get(url=self.base_url)

        session_hash_match = re.search(r'"apiUrl":"\\/api\?hash=(\w+)"', response.text)
        if session_hash_match is None:
            raise FragmentError("No session hash")
        self._session.hash = session_hash_match.group(1)

        ton_proof_match = re.search(r'"ton_proof":"(.+?)"', response.text)
        if ton_proof_match is None:
            raise FragmentError("No ton proof")
        self._session.ton_proof = ton_proof_match.group(1)

        ton_rate_match = re.search(r'"tonRate":([0-9.]+)', response.text)
        if ton_rate_match:
            self._ton_rate = float(ton_rate_match.group(1))

    async def request(
        self,
        method: str,
        data: dict,
        headers: dict | None = None,
        cookies: dict | None = None,
        authorize: bool = True,
    ) -> dict:
        if authorize:
            await self.authorize()

        if self._session.hash is None:
            raise FragmentError("No session hash")

        response = await self.client.post(
            url=f"{self.base_url}/api?hash={self._session.hash}",
            data={"method": method, **data},
            headers=headers,
            cookies=cookies,
        )

        if response.status_code != 200:
            log.warning("Status code is not 200", status_code=response.status_code)

        data_json = response.json()

        if data_json.get("error"):
            log.warning("Bad fragment request", json=data_json)
            raise FragmentBadRequest(data_json["error"])

        return data_json

    @property
    def client(self) -> AsyncClient:
        if self._client is None:
            self._client = AsyncClient(
                headers={
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
                },
                cookies=self._session.cookies,
            )
        return self._client

    def save_session(self) -> None:
        for cookie in self.client.cookies.jar:
            self._session.cookies[cookie.name] = cookie.value

        with open(settings.FRAGMENT_SESSION_PATH, "w") as fo:
            json.dump(self._session.model_dump(), fo, indent=2)

    def load_session(self) -> FragmentSession:
        return FragmentSession(cookies={"stel_dt": "-180"})

        try:
            with open(settings.FRAGMENT_SESSION_PATH) as fr:
                session = FragmentSession.model_validate(json.load(fr))
                session.cookies["stel_dt"] = "-180"
        except Exception as exc:
            log.warning("Error loading session", error=str(exc))
            session = FragmentSession(cookies={"stel_dt": "-180"})

        return session

    async def get_stars_buy_page(self):
        response = await self.client.get(
            f"{self.base_url}/stars/buy",
            headers={"X-Requested-With": "XMLHttpRequest"},
        )

        return response.json()

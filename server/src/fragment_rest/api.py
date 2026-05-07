import re
from typing import Any

from httpx import AsyncClient

from src.fragment_rest.exceptions import (
    FragmentAPIAccessDenied,
    FragmentAPIBadRequest,
    FragmentAPIPageError,
    FragmentAPIUsersNotFound,
)
from src.fragment_rest.models import MainPageTokens


class FragmentAPIClient:
    SESSION_REFRESH_LT = 60 * 60 * 3  # 3 hours
    RELEVANT_COOKIES = ["stel_dt", "stel_ssid", "stel_token", "stel_ton_token"]

    def __init__(
        self,
        initial_cookies: dict | None = None,
        *,
        base_url: str = "https://fragment.com/",
    ) -> None:
        self.base_url = base_url
        self._client: AsyncClient = AsyncClient(
            headers={
                "Origin": self.base_url,
                "Referer": self.base_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
            },
            cookies=initial_cookies,
            http2=True,
        )

    async def request(
        self,
        hash: str,
        method: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if headers is None:
            headers = {}

        # must always be like this for requests
        headers["X-Requested-With"] = "XMLHttpRequest"

        response = await self._client.post(
            url=f"{self.base_url}/api?hash={hash}",
            data={"method": method, **data},
            headers=headers,
            cookies=cookies,
        )

        if response.status_code != 200:
            raise FragmentAPIBadRequest()

        json = response.json()

        if "error" in json:
            if json["error"].startswith("No Telegram users found"):
                raise FragmentAPIUsersNotFound(json["error"])
            if json["error"].startswith("Access denied"):
                raise FragmentAPIAccessDenied(json["error"])
            raise FragmentAPIBadRequest(json["error"])

        return json

    async def get_main_page_tokens(self) -> MainPageTokens:
        response = await self._client.get(url=self.base_url)

        if response.status_code != 200:
            raise FragmentAPIPageError("Main page unavailable")

        session_hash_match = re.search(r'"apiUrl":"\\/api\?hash=(\w+)"', response.text)
        if session_hash_match is None:
            raise FragmentAPIPageError("No session hash match")
        session_hash = session_hash_match.group(1)

        ton_proof_match = re.search(r'"ton_proof":"(.+?)"', response.text)
        if ton_proof_match is None:
            raise FragmentAPIPageError("No ton proof match")
        session_ton_proof = ton_proof_match.group(1)

        ton_rate_match = re.search(r'"tonRate":(\d+.?\d+)', response.text)
        if ton_rate_match is None:
            raise FragmentAPIPageError("No ton rate")
        ton_rate_match = float(ton_rate_match.group(1))

        return MainPageTokens(
            hash=session_hash,
            ton_proof_payload=session_ton_proof,
            ton_rate=ton_rate_match,
        )

    def get_client_relevant_cookies(self) -> dict[str, str]:
        all_cookies = {}

        for cookie in self._client.cookies.jar:
            if cookie.name.lower() in self.RELEVANT_COOKIES:
                all_cookies[cookie.name] = cookie.value

        return all_cookies

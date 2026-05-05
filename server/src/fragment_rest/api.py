from typing import Any

from httpx import AsyncClient

from src.fragment_rest.exceptions import (
    FragmentAPIAccessDenied,
    FragmentAPIBadRequest,
    FragmentAPIError,
    FragmentAPIUsersNotFound,
)


class FragmentAPIClient:
    SESSION_REFRESH_LT = 60 * 60 * 3  # 3 hours
    RELEVANT_COOKIES = ["stel_dt", "stel_ssid", "stel_token", "stel_ton_token"]

    def __init__(self, initial_cookies: dict | None = None) -> None:
        self.base_url = "https://fragment.com/"

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

    async def get_main_page(self) -> str:
        response = await self._client.get(url=self.base_url)

        if response.status_code != 200:
            raise FragmentAPIError()

        return response.text

    def get_client_relevant_cookies(self) -> dict[str, str]:
        all_cookies = {}

        for cookie in self._client.cookies.jar:
            if cookie.name.lower() in self.RELEVANT_COOKIES:
                all_cookies[cookie.name] = cookie.value

        return all_cookies

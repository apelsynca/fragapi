from typing import Any

from httpx import AsyncClient

from src.fragment_rest.exceptions import (
    FragmentAPIBadRequest,
    FragmentAPIError,
    FragmentAPIUsersNotFound,
)


class FragmentAPIClient:
    SESSION_REFRESH_LT = 60 * 60 * 3  # 3 hours
    RELEVANT_COOKIES = ["stel_dt", "stel_ssid", "stel_token", "stel_ton_token"]

    def __init__(self, initial_cookies: dict | None = None) -> None:
        self.base_url = "https://fragment.com/"

        self._default_headers = {"Origin": self.base_url, "Referer": self.base_url}
        self._client: AsyncClient = AsyncClient(
            headers=self._default_headers, cookies=initial_cookies
        )

    async def request(
        self,
        hash: str,
        method: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
    ) -> dict[str, Any]:
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

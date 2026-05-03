from typing import Any

from httpx import AsyncClient

from src.fragment_rest.exceptions import (
    FragmentAPIBadRequest,
    FragmentAPIError,
    FragmentAPINotAuthorized,
    FragmentAPIUsersNotFound,
)
from src.fragment_rest.models import FragmentSession
from src.kit.ton_connect import TonConnect


class FragmentAPIClient:
    TC_DOMAIN = "fragment.com"

    def __init__(self, ton_connect: TonConnect) -> None:
        if ton_connect.tc_domain != self.TC_DOMAIN:
            raise RuntimeError(
                f"ton_connect.tc_domain is different from required {self.TC_DOMAIN}."
            )

        self.base_url = "https://fragment.com/"
        self._ton_connect = ton_connect

        self._default_headers = {"Origin": self.base_url, "Referer": self.base_url}
        self._client: AsyncClient = AsyncClient(headers=self._default_headers)

        self._session: FragmentSession | None = None

    async def request(
        self,
        method: str,
        data: dict,
        headers: dict | None = None,
        *,
        check_authorized: bool = True,
    ) -> dict[str, Any]:
        if self._session is None:
            raise FragmentAPINotAuthorized("no session")

        response = await self._client.post(
            url=f"{self.base_url}/api?hash={self._session.hash}",
            data={"method": method, **data},
            headers=headers,
            # cookies=cookies,
        )

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

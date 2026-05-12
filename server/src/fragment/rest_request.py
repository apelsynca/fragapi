from abc import ABC, abstractmethod

from httpx import AsyncClient

FragCookies = dict[str, str]


class BaseClient(ABC):
    @abstractmethod
    async def do_request(
        self,
        url: str,
        method: str,
        form_data: dict | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, bytes]:
        raise NotImplementedError()

    @abstractmethod
    def extract_cookies(self) -> FragCookies:
        raise NotImplementedError()


class HttpxClient(BaseClient):
    def __init__(self, **client_kwargs) -> None:
        self._client = AsyncClient(**client_kwargs)

    async def do_request(
        self,
        url: str,
        method: str,
        form_data: dict | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, bytes]:
        response = await self._client.request(
            method=method, url=url, data=form_data, headers=headers
        )

        return response.status_code, response.content

    def extract_cookies(self) -> FragCookies:
        return dict(self._client.cookies.items())

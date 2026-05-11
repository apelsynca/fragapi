from abc import ABC, abstractmethod
from typing import Any

from httpx import AsyncClient


class BaseRequest(ABC):
    @abstractmethod
    async def do_request(
        self, url: str, method: str, json_data: dict | None = None
    ) -> tuple[int, Any, dict[str, str]]:
        raise NotImplementedError()


class HttpxRequest(BaseRequest):
    def __init__(self) -> None:
        self._client = AsyncClient()

    async def do_request(
        self, url: str, method: str, json_data: dict | None = None
    ) -> tuple[int, bytes, dict[str, str]]:
        response = await self._client.request(method=method, url=url, json=json_data)

        return response.status_code, response.content, dict(response.cookies.items())

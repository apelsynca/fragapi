from time import time
from typing import Any

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.session_manager import FragmentSessionManager
from src.kit.ton_connect import TonConnect
from src.logging import get_logger

log = get_logger()


class BaseFragmentRest:
    SESSION_CHECK_DELTA: int = 60 * 60 * 3  # 3 hours

    def __init__(self, ton_connect: TonConnect) -> None:
        self._api = FragmentAPIClient()
        self._session_manager = FragmentSessionManager()
        self._tc = ton_connect

    async def start(self) -> None:
        pass

    async def ensure_fresh_session(self) -> None:
        now = time()

    async def _request(self, method: str, data: dict[str, Any]) -> dict[str, Any]:
        session = self._session_manager.get_session()
        if session is None:
            raise RuntimeError(
                "Fragment session is not present in the FragmentRest. "
                "Are you sure you called FragmentRest.start method?"
            )

        await self.ensure_fresh_session()

        return await self._api.request(
            hash=session.hash,
            method=method,
            data=data,
            cookies=session.cookies,
        )

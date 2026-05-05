import json
from time import time
from typing import Any

from src.config import settings
from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.fragment_rest.models import FragmentSession
from src.kit.ton_connect import TonConnect
from src.logging import get_logger

log = get_logger()


class FragmentRest:
    SESSION_LT: int = 60 * 60 * 3  # 3 hours

    def __init__(self, ton_connect: TonConnect) -> None:
        self._api = FragmentAPIClient()
        self._auth = FragmentRestAuth(ton_connect=ton_connect)
        self._session: FragmentSession | None = self._load_session()

        self._last_session_check: float = 0

    async def start(self) -> None:
        await self.refresh_session()

    async def ensure_fresh_session(self) -> None:
        now = time()

        if now - self._last_session_check < self.SESSION_LT:
            return

        await self.refresh_session()

    async def refresh_session(self) -> None:
        need_to_authorize = True

        if self._session is not None:
            need_to_authorize = await self._auth.check_session(
                api_client=self._api, session=self._session
            )

        if need_to_authorize:
            new_session = await self._auth.authorize(api_client=self._api)

            self._session = new_session

    async def _request(self, method: str, data: dict[str, Any]) -> None:
        if self._session is None:
            raise RuntimeError(
                "Fragment session is not present in the client state. "
                "Are you sure you called FragmentRest.start method?"
            )

        await self.ensure_fresh_session()

        await self._api.request(
            hash=self._session.hash,
            method=method,
            data=data,
            cookies=self._session.cookies,
        )

    def _load_session(self) -> FragmentSession | None:
        try:
            with open(settings.FRAGMENT_SESSION_PATH) as fr:
                raw = json.load(fr)
                session = FragmentSession(
                    hash=raw["hash"],
                    ton_proof_payload=raw["ton_proof_payload"],
                    cookies=raw["cookies"],
                )
                session.cookies["stel_dt"] = "-180"
                return session
        except FileNotFoundError:
            log.error(
                "Fragment session file not found", path=settings.FRAGMENT_SESSION_PATH
            )
            raise
        except KeyError as exc:
            log.error("Key error while loading the fragment session")
            raise
        except Exception as exc:
            log.error("Error loading session", error=str(exc))
            raise

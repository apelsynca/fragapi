import json

import structlog
from pydantic import BaseModel, ValidationError

from src.config import settings
from src.integrations.fragment.models import MainPageTokens
from src.logging import Logger

log: Logger = structlog.get_logger()


class FragmentSession(BaseModel):
    hash: str
    ton_proof_payload: str
    cookies: dict[str, str]


class SessionStorage:
    def __init__(self, session_key: str) -> None:
        # self._session_key = session_key
        self.session: FragmentSession | None = None

    def load(self) -> None:
        try:
            with open(settings.FRAGMENT_SESSION_PATH) as fr:
                json_str = fr.read()
                self.session = FragmentSession.model_validate_json(json_str)
        except FileNotFoundError as exc:
            log.error(
                "Fragment Session file is not found!",
                session_path=settings.FRAGMENT_SESSION_PATH,
            )
            raise exc
        except ValidationError as e:
            log.warning("Session file validation error", error=str(e))

    def save(self) -> None:
        if self.session is None:
            raise ValueError("There is no session to save")

        with open(settings.FRAGMENT_SESSION_PATH, "w") as fw:
            json.dump(self.session.model_dump(), fw, indent=2)

    def save_cookies(self, cookies: dict[str, str]) -> None:
        if self.session is None:
            raise RuntimeError("No session")

        self.session.cookies.update(cookies)

    def save_tokens(self, tokens: MainPageTokens) -> None:
        """
        Saves main page tokens in the session,
        if session is None -> Creates a new one
        """

        if self.session is None:
            self.session = FragmentSession(
                hash=tokens.hash, ton_proof_payload=tokens.ton_proof_payload, cookies={}
            )
            return

        self.session.hash = tokens.hash
        self.session.ton_proof_payload = tokens.ton_proof_payload

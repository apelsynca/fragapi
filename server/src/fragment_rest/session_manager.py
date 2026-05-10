import json

from pydantic import ValidationError

from src.config import settings
from src.fragment_rest.exceptions import FragmentAPIError
from src.fragment_rest.models import FragmentSession, MainPageTokens
from src.logging import get_logger

log = get_logger()


class FragmentSessionManager:
    def __init__(self) -> None:
        self._session: FragmentSession | None = None

    def is_valid_session(self) -> bool:
        if self._session is None:
            raise FragmentAPIError()

        if len(self._session.hash) != 18:
            return False
        if len(self._session.ton_proof_payload) != 18:
            return False

        return True

    def get_session(self) -> FragmentSession | None:
        return self._session

    def set_session(self, session: FragmentSession) -> None:
        self._session = session

        if not self.is_valid_session():
            self._session = None
            raise FragmentAPIError("Cannot set invalid session")

    def check_tokens(self, tokens: MainPageTokens) -> bool:
        """Call it after getting main page data"""

        if self._session is None:
            raise RuntimeError("Need to set session")

        if self._session.hash != tokens.hash:
            return False

        if self._session.ton_proof_payload != tokens.ton_proof_payload:
            return False

        return True

    def load_saved(self) -> None:
        try:
            with open(settings.FRAGMENT_SESSION_PATH) as fr:
                try:
                    raw = json.load(fr)
                except json.JSONDecodeError:
                    raise RuntimeError("Runtime")

                try:
                    self._session = FragmentSession.model_validate(raw)
                except ValidationError:
                    raise RuntimeError("Runtime")
        except Exception as exc:
            log.error("Error loading session", error=str(exc))
            raise

    # here save session

    """
    def _save_session(self, session: FragmentSession) -> None:
        with open(settings.FRAGMENT_SESSION_PATH, "w") as fw:
            json.dump(
                {
                    "hash": session.hash,
                    "ton_proof_payload": session.ton_proof_payload,
                    "cookies": session.cookies,
                    "last_session_check": session.last_session_check,
                },
                fw,
                indent=2,
            )
    """

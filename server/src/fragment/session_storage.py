from pydantic import BaseModel

from src.fragment.types import MainPageTokens


class FragmentSession(BaseModel):
    hash: str
    ton_proof_payload: str
    cookies: dict[str, str]


class SessionStorage:
    def __init__(self, session_key: str) -> None:
        self._session_key = session_key
        self.session: FragmentSession | None = None

    def load_session(self) -> None:
        raise RuntimeError("OH SHIT IM LOADING THE SESSION")

    def save_cookies(self, cookies: dict[str, str]) -> None:
        if self.session is None:
            raise RuntimeError("No session")

        self.session.cookies.update(cookies)

    def save_tokens(self, tokens: MainPageTokens) -> None:
        if self.session is None:
            self.session = FragmentSession(
                hash=tokens.hash, ton_proof_payload=tokens.ton_proof_payload, cookies={}
            )
            return

        self.session.hash = tokens.hash
        self.session.ton_proof_payload = tokens.ton_proof_payload

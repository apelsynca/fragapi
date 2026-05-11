from pydantic import BaseModel


class FragmentSession(BaseModel):
    hash: str
    ton_proof_payload: str
    cookies: dict[str, str]


class SessionStorage:
    def __init__(self, session_key: str) -> None:
        self.session: FragmentSession | None = None

    def load_session(self) -> None:
        raise RuntimeError("OH SHIT IM LOADING THE SESSION")

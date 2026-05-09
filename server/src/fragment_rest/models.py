from dataclasses import dataclass


@dataclass
class FragmentSession:
    hash: str
    ton_proof_payload: str
    cookies: dict[str, str]
    last_session_check: float = 0


@dataclass
class MainPageTokens:
    hash: str
    ton_proof_payload: str
    ton_rate: float

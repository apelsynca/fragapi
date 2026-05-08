from dataclasses import dataclass


@dataclass
class FragmentSession:
    hash: str
    ton_proof_payload: str
    cookies: dict[str, str]


@dataclass
class MainPageTokens:
    hash: str
    ton_proof_payload: str
    ton_rate: float

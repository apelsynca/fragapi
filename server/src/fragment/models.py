from dataclasses import dataclass


@dataclass
class MainPageTokens:
    hash: str
    ton_proof_payload: str
    ton_rate: float

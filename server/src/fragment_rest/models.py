from dataclasses import dataclass


@dataclass
class FragmentSession:
    hash: str
    ton_proof_payload: str
    cookies: dict[str, str]

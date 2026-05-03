from dataclasses import dataclass


@dataclass
class FragmentSession:
    hash: str
    ton_proof: str
    cookies: dict[str, str]

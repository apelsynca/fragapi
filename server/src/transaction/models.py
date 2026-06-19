from dataclasses import dataclass
from typing import Literal


@dataclass
class FTMetadata:
    recipient: str
    recipient_username: str
    stars_amount: int | None = None
    premium_months: Literal[3, 6, 12] | None = None

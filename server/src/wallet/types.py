from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.kit.ton_connect import TonConnectMessage


class TonConnectTransaction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    valid_until: Annotated[datetime, Field(alias="validUntil")]
    from_address: Annotated[str, Field(alias="from")]
    messages: list[TonConnectMessage]

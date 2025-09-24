from pydantic import BaseModel, ConfigDict

from src.ton_connect.types import TonConnectTransaction


class FragmentSession(BaseModel):
    hash: str | None = None
    ton_proof: str | None = None
    cookies: dict = {}


class APISchema(BaseModel):
    model_config = ConfigDict(extra="ignore")


class RecipientFound(APISchema):
    myself: bool
    recipient: str
    photo: str
    name: str


class FragmentRecipient(APISchema):
    ok: bool
    found: RecipientFound


class BuyRequest(APISchema):
    req_id: str
    myself: bool
    amount: float


class BuyStarsRequest(BuyRequest):
    to_bot: bool


class BuyPremiumRequest(BuyRequest):
    pass


class FragmentLink(APISchema):
    ok: bool
    transaction: TonConnectTransaction

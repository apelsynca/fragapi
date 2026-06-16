from decimal import Decimal

from pydantic import BaseModel

from src.kit.ton_connect import TonConnectTransaction


class FragmentAPIObject(BaseModel):
    pass


class FragmentAPIResponseObject(FragmentAPIObject):
    ok: bool


class FoundRecipientData(FragmentAPIObject):
    myself: bool
    recipient: str
    photo: str
    name: str


class RecipientData(FragmentAPIResponseObject):
    found: FoundRecipientData


class BuyRequest(FragmentAPIObject):
    req_id: str
    myself: bool
    amount: Decimal


class BuyLink(FragmentAPIResponseObject):
    transaction: TonConnectTransaction
    confirm_method: str | None = None

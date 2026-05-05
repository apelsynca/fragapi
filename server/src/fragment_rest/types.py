from pydantic import BaseModel

from src.wallet.types import TonConnectTransaction


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
    amount: float


class BuyLink(FragmentAPIResponseObject):
    transaction: TonConnectTransaction
    confirm_method: str

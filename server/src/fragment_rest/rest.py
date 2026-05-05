from typing import Literal

from src.fragment_rest.base_rest import BaseFragmentRest
from src.fragment_rest.types import BuyLink, BuyRequest, RecipientData

type MonthsAmount = Literal["3", "6", "12"]


class FragmentRest(BaseFragmentRest):
    async def search_stars_recipient(
        self, query: str, quantity: int | None = None
    ) -> RecipientData:
        data = await self._request(
            method="searchStarsRecipient",
            data={"query": query, "quantity": quantity if quantity is not None else ""},
        )
        return RecipientData.model_validate(data)

    async def init_buy_stars_request(self, recipient: str, quantity: int) -> BuyRequest:
        data = await self._request(
            method="initBuyStarsRequest",
            data={"recipient": recipient, "quantity": str(quantity)},
        )
        return BuyRequest.model_validate(data)

    async def get_buy_stars_link(
        self, req_id: str, *, transaction: bool = True, show_sender: bool = False
    ) -> BuyLink:
        return await self.get_buy_link(
            method="getBuyStarsLink",
            req_id=req_id,
            transaction=transaction,
            show_sender=show_sender,
        )

    async def search_premium_gift_recipient(
        self, query: str, months: MonthsAmount = "12"
    ) -> RecipientData:
        data = await self._request(
            method="searchPremiumGiftRecipient",
            data={"query": query, "months": months},
        )
        return RecipientData.model_validate(data)

    async def init_gift_premium_request(
        self, recipient: str, months: MonthsAmount
    ) -> BuyRequest:
        data = await self._request(
            method="initGiftPremiumRequest",
            data={"recipient": recipient, "months": months},
        )
        return BuyRequest.model_validate(data)

    async def get_gift_premium_link(
        self, req_id: str, *, transaction: bool = True, show_sender: bool = False
    ) -> BuyLink:
        return await self.get_buy_link(
            method="getGiftPremiumLink",
            req_id=req_id,
            transaction=transaction,
            show_sender=show_sender,
        )

    async def get_buy_link(
        self,
        method: Literal["getBuyStarsLink", "getGiftPremiumLink"],
        req_id: str,
        *,
        transaction: bool = True,
        show_sender: bool = False,
    ) -> BuyLink:
        account = self._auth.ton_connect.get_account()
        device = self._auth.ton_connect.get_device()

        # need account and device here (no proof)
        data = await self._request(
            method=method,
            data={
                "account": account,
                "device": device,
                "transaction": int(transaction),
                "id": req_id,
                "show_sender": int(show_sender),
            },
        )

        return BuyLink.model_validate(data)

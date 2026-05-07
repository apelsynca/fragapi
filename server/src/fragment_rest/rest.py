from time import time
from typing import Literal

from src.fragment_rest.base_rest import BaseFragmentRest
from src.fragment_rest.exceptions import FragmentAPIPageError
from src.fragment_rest.types import BuyLink, BuyRequest, RecipientData
from src.kit.ton_connect import TonConnect

type MonthsAmount = Literal["3", "6", "12"]


class FragmentRest(BaseFragmentRest):
    def __init__(self, ton_connect: TonConnect) -> None:
        self._ton_rate_ut: float = 0
        self._cached_ton_rate: float | None = None

        super().__init__(ton_connect)

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

    async def get_ton_rate(self) -> float:
        now = time()
        if self._cached_ton_rate is None or now - self._ton_rate_ut > 0:
            try:
                main_page_tokens = await self._api.get_main_page_tokens()
            except FragmentAPIPageError as e:
                if self._cached_ton_rate:
                    return self._cached_ton_rate
                raise e
            self._cached_ton_rate = main_page_tokens.ton_rate

        return self._cached_ton_rate

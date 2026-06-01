import random
from time import time
from typing import Literal

from src.integrations.fragment.rest_client import FragmentRestClient
from src.integrations.fragment.types import BuyLink, BuyRequest, RecipientData

type MonthsAmount = Literal["3", "6", "12"]


class Fragment:
    CACHE_LT = 60 * 5  # 10 mins

    def __init__(self, clients: list[FragmentRestClient]) -> None:
        if len(clients) == 0:
            raise RuntimeError("Fragment requires at least 1 client")

        self.clients = clients

        self._last_cache_ut: float = 0
        self._cached_ton_rate: float | None = None

    async def get_ton_usd_rate(self) -> float:
        now = time()
        if (
            now - self._last_cache_ut <= self.CACHE_LT
            and self._cached_ton_rate is not None
        ):
            return self._cached_ton_rate

        client = self.get_client()
        main_page_tokens = await client.get_main_page_tokens()

        return main_page_tokens.ton_rate

    async def search_stars_recipient(
        self, query: str, quantity: int | None = None
    ) -> RecipientData:
        client = self.get_client()

        data = await client.api_request(
            method="searchStarsRecipient",
            data={
                "query": query,
                "quantity": str(quantity) if quantity is not None else "",
            },
        )
        return RecipientData.model_validate(data)

    async def init_buy_stars_request(
        self, recipient: str, quantity: int, *, payment_method: Literal["ton"] = "ton"
    ) -> BuyRequest:
        client = self.get_client()

        data = await client.api_request(
            method="initBuyStarsRequest",
            data={
                "recipient": recipient,
                "quantity": str(quantity),
                "payment_method": payment_method,
            },
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
        client = self.get_client()

        data = await client.api_request(
            method="searchPremiumGiftRecipient",
            data={"query": query, "months": months},
        )
        return RecipientData.model_validate(data)

    async def init_gift_premium_request(
        self,
        recipient: str,
        months: MonthsAmount,
        *,
        payment_method: Literal["ton"] = "ton",
    ) -> BuyRequest:
        client = self.get_client()

        data = await client.api_request(
            method="initGiftPremiumRequest",
            data={
                "recipient": recipient,
                "months": months,
                "payment_method": payment_method,
            },
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
        client = self.get_client()

        # sometimes bad text -> "Session expired"

        data = await client.api_request(
            method=method,
            data={
                "id": req_id,
                "transaction": str(int(transaction)),
                "show_sender": str(int(show_sender)),
            },
        )

        return BuyLink.model_validate(data)

    def get_client(self) -> FragmentRestClient:
        return random.choice(self.clients)

import json
from typing import Literal

from src.fragment.rest_client import FragmentRestClient
from src.fragment.types import BuyLink, BuyRequest, RecipientData

type MonthsAmount = Literal["3", "6", "12"]


class Fragment:
    def __init__(self, clients: list[FragmentRestClient]) -> None:
        if len(clients) == 0:
            raise RuntimeError("Fragment needs at least 1 client")

        self.clients = clients

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

    async def init_buy_stars_request(self, recipient: str, quantity: int) -> BuyRequest:
        client = self.get_client()

        data = await client.api_request(
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
        client = self.get_client()

        data = await client.api_request(
            method="searchPremiumGiftRecipient",
            data={"query": query, "months": months},
        )
        return RecipientData.model_validate(data)

    async def init_gift_premium_request(
        self, recipient: str, months: MonthsAmount
    ) -> BuyRequest:
        client = self.get_client()

        data = await client.api_request(
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
        client = self.get_client()

        # need account and device here (no proof)
        account = json.dumps(client._ton_connect.get_account(), separators=(",", ":"))
        device = json.dumps(client._ton_connect.get_device(), separators=(",", ":"))

        data = await client.api_request(
            method=method,
            data={
                "account": account,
                "device": device,
                "transaction": str(int(transaction)),
                "id": req_id,
                "show_sender": str(int(show_sender)),
            },
        )

        return BuyLink.model_validate(data)

    def get_client(self) -> FragmentRestClient:
        # TODO: normal random piper algorithm or whatever it called
        return self.clients[0]

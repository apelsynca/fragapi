import json

from src.fragment.enums import PremiumMonths
from src.kit.utils import utc_now

from .base import BaseFragment
from .types import BuyPremiumRequest, BuyStarsRequest, FragmentLink, FragmentRecipient


class Fragment(BaseFragment):
    """
    Interaction with fragment methods, supporting type-hinting
    """

    def __init__(self, base_url: str = "https://fragment.com") -> None:
        super().__init__(base_url=base_url)

        self._last_ton_rate_update = utc_now()

    async def get_ton_rate(self) -> float:
        last_update_delta = utc_now() - self._last_ton_rate_update

        if last_update_delta.total_seconds() < 30 and self._ton_rate:
            return self._ton_rate

        buy_page = await self.get_stars_buy_page()
        self._ton_rate = float(buy_page["s"]["tonRate"])

        return self._ton_rate

    async def search_stars_recipient(
        self, query: str, quantity: int | None = None
    ) -> FragmentRecipient:
        data = await self.request(
            method="searchStarsRecipient",
            data={"query": query, "quantity": str(quantity) if quantity else ""},
        )

        return FragmentRecipient.model_validate(data)

    async def init_buy_stars_request(
        self, recipient: str, quantity: int
    ) -> BuyStarsRequest:
        data = await self.request(
            method="initBuyStarsRequest",
            data={"recipient": recipient, "quantity": str(quantity)},
        )
        return BuyStarsRequest.model_validate(data)

    async def get_buy_stars_link(
        self, req_id: str, show_sender: bool = False
    ) -> FragmentLink:
        return await self.get_buy_link(
            method="getBuyStarsLink", req_id=req_id, show_sender=show_sender
        )

    async def search_premium_recipient(
        self, query: str, months: PremiumMonths = PremiumMonths.YEAR
    ) -> FragmentRecipient:
        data = await self.request(
            method="searchPremiumGiftRecipient", data={"query": query, "months": months}
        )

        return FragmentRecipient.model_validate(data)

    async def init_premium_request(
        self, recipient: str, months: PremiumMonths
    ) -> BuyPremiumRequest:
        data = await self.request(
            method="initGiftPremiumRequest",
            data={"recipient": recipient, "months": months},
        )
        return BuyPremiumRequest.model_validate(data)

    async def get_premium_link(
        self, req_id: str, show_sender: bool = False
    ) -> FragmentLink:
        return await self.get_buy_link(
            method="getGiftPremiumLink", req_id=req_id, show_sender=show_sender
        )

    async def get_buy_link(
        self, method: str, req_id: str, show_sender: bool = False
    ) -> FragmentLink:
        data = await self.request(
            method=method,
            data={
                "account": json.dumps(self.tc.get_account()),
                "device": json.dumps(self.tc.get_device()),
                "transaction": 1,
                "id": req_id,
                "show_sender": int(show_sender),
            },
        )
        return FragmentLink.model_validate(data)


fragment = Fragment()

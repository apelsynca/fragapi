import asyncio

import structlog

from src.enums import FragmentTransactionReason, PremiumMonths
from src.exceptions import FragError, ResourceNotFound
from src.fragment_transaction.models import FTMetadata
from src.fragment_transaction.service import (
    fragment_transaction as fragment_transaction_service,
)
from src.integrations.fragment import Fragment
from src.integrations.fragment.exceptions import FragmentAPIUsersNotFound
from src.logging import Logger
from src.models import User
from src.postgres import AsyncSession
from src.premium.schemas import BuyPremium, BuyPremiumResponse, PremiumRecipient

log: Logger = structlog.get_logger()


class PremiumService:
    async def buy(
        self,
        session: AsyncSession,
        user: User,
        data: BuyPremium,
        fragment: Fragment,
    ) -> BuyPremiumResponse:
        log.debug("premium.buy called", months=data.months, username=data.username)

        recipient_data = await self.get_recipient(
            fragment, username=data.username, months=data.months
        )

        buy_request = await fragment.init_gift_premium_request(
            recipient=recipient_data.recipient, months=data.months.value
        )
        await asyncio.sleep(0.05)

        buy_link = await fragment.get_gift_premium_link(req_id=buy_request.req_id)
        log.debug("premium.buy got link", buy_link=buy_link)

        if not buy_link.ok:
            raise FragError("Buy link that we recieved is invalid")

        tc_transaction = buy_link.transaction

        fragment_transaction = await fragment_transaction_service.send_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=FragmentTransactionReason.premium,
            metadata=FTMetadata(
                recipient=recipient_data.recipient,
                recipient_username=data.username,
                premium_months=data.months.value,
            ),
        )

        return BuyPremiumResponse(
            message_hash=fragment_transaction.ton_transaction.message_hash,
            transaction_id=fragment_transaction.id,
            photo=recipient_data.photo,
            name=recipient_data.name,
            amount=fragment_transaction.amount,
        )

    async def get_recipient(
        self,
        fragment: Fragment,
        username: str,
        *,
        months: PremiumMonths = PremiumMonths.YEAR,
    ) -> PremiumRecipient:
        try:
            recipient = await fragment.search_premium_gift_recipient(
                query=username, months=months.value
            )
        except FragmentAPIUsersNotFound:
            raise ResourceNotFound("User is not found")

        return PremiumRecipient(
            recipient=recipient.found.recipient,
            photo=recipient.found.photo,
            name=recipient.found.name,
        )


premium = PremiumService()

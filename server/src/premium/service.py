import asyncio

import structlog

from src.caching import premium_recipient_cache
from src.enums import PremiumMonths, TransactionReason
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.integrations.fragment import Fragment
from src.integrations.fragment.exceptions import (
    FragmentAPIAccessDenied,
    FragmentAPIError,
    FragmentAPINotAUser,
    FragmentAPIUsersNotFound,
)
from src.logging import Logger
from src.models import User
from src.postgres import AsyncSession
from src.premium.schemas import BuyPremium, BuyPremiumResponse, PremiumRecipient
from src.redis import Redis
from src.transaction.models import FTMetadata
from src.transaction.service import transaction as transaction_service

log: Logger = structlog.get_logger()


class PremiumService:
    async def buy(
        self,
        session: AsyncSession,
        user: User,
        data: BuyPremium,
        fragment: Fragment,
        redis: Redis,
    ) -> BuyPremiumResponse:
        log.debug("premium.buy called", months=data.months, username=data.username)

        recipient_data = await self.get_recipient(
            fragment, username=data.username, redis=redis, months=data.months
        )

        buy_request = await fragment.init_gift_premium_request(
            recipient=recipient_data.recipient, months=data.months.value
        )
        await asyncio.sleep(0.05)

        buy_link = await fragment.get_gift_premium_link(
            req_id=buy_request.req_id, show_sender=data.show_sender
        )
        log.debug("premium.buy got link", buy_link=buy_link)

        if not buy_link.ok:
            raise FragError("Buy link that we recieved is invalid")

        tc_transaction = buy_link.transaction

        transaction = await transaction_service.send_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=TransactionReason.premium,
            metadata=FTMetadata(
                recipient=recipient_data.recipient,
                recipient_username=data.username,
                premium_months=data.months.value,
            ),
        )

        return BuyPremiumResponse(
            message_hash=transaction.ton_transaction.message_hash,
            transaction_id=transaction.id,
            photo=recipient_data.photo,
            name=recipient_data.name,
            amount=transaction.amount,
        )

    async def get_recipient(
        self,
        fragment: Fragment,
        username: str,
        redis: Redis,
        *,
        months: PremiumMonths = PremiumMonths.YEAR,
    ) -> PremiumRecipient:
        base_recipient = await premium_recipient_cache.get(
            redis=redis, username=username
        )

        if base_recipient is not None:
            return PremiumRecipient.model_validate(base_recipient)

        try:
            recipient_data = await fragment.search_premium_gift_recipient(
                query=username, months=months.value
            )
        except (FragmentAPIUsersNotFound, FragmentAPINotAUser):
            raise ResourceNotFound("User is not found")
        except FragmentAPIAccessDenied:
            raise FragError(
                "Oops, we somehow lost the access to fragment. "
                "Please wait a little or contact support!"
            )
        except FragmentAPIError as exc:
            log.warning("premium.get_recipient fragment api error", message=exc.message)
            raise BadRequest("Unknown error for us from fragment side")

        recipient = PremiumRecipient(
            recipient=recipient_data.found.recipient,
            photo=recipient_data.found.photo,
            name=recipient_data.found.name,
        )

        await premium_recipient_cache.set(
            redis=redis, recipient=recipient, username=username
        )

        return recipient


premium = PremiumService()

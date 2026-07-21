import asyncio
import random

import structlog

from src.enums import TransactionReason
from src.exceptions import (
    BadRequest,
    FragError,
    FragRequestValidationError,
    ResourceNotFound,
)
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
from src.stars.schemas import BuyStars, BuyStarsResponse, StarsRecipient
from src.transaction.models import FTMetadata
from src.transaction.service import transaction as transaction_service

log: Logger = structlog.get_logger()


class StarsService:
    async def buy(
        self,
        session: AsyncSession,
        user: User,
        data: BuyStars,
        fragment: Fragment,
    ) -> BuyStarsResponse:
        log.debug("stars.buy", quantity=data.quantity, username=data.username)

        if len(data.username) < 3:
            raise FragRequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "username"),
                        "msg": "stars buy request must have a username with length bigger than 3",
                        "input": data.username,
                    }
                ]
            )

        recipient_data = await self.get_recipient(
            fragment=fragment, username=data.username, quantity=data.quantity
        )
        await asyncio.sleep(0.05)

        buy_request = await fragment.init_buy_stars_request(
            recipient=recipient_data.recipient, quantity=data.quantity
        )
        await asyncio.sleep(0.05)

        buy_link = await fragment.get_buy_stars_link(
            req_id=buy_request.req_id, show_sender=data.show_sender
        )
        log.debug("stars.buy got link", buy_link=buy_link)

        if not buy_link.ok:
            raise FragError("Buy link that we recieved is invalid")

        tc_transaction = buy_link.transaction

        transaction = await transaction_service.send_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=TransactionReason.stars,
            metadata=FTMetadata(
                recipient=recipient_data.recipient,
                recipient_username=data.username,
                stars_amount=data.quantity,
            ),
        )

        return BuyStarsResponse(
            message_hash=transaction.ton_transaction.message_hash,
            transaction_id=transaction.id,
            photo=recipient_data.photo,
            name=recipient_data.name,
            amount=transaction.amount,
        )

    async def get_recipient(
        self, fragment: Fragment, username: str, *, quantity: int | None = None
    ) -> StarsRecipient:
        try:
            recipient = await fragment.search_stars_recipient(
                query=username,
                quantity=random.choice([50, 75, 500, 2500])
                if quantity is None
                else quantity,
            )
        except (FragmentAPIUsersNotFound, FragmentAPINotAUser):
            raise ResourceNotFound("User is not found")
        except FragmentAPIAccessDenied:
            raise FragError(
                "Oops, we somehow lost the access to fragment. "
                "Please wait a little or contact support!"
            )
        except FragmentAPIError as exc:
            log.warning("stars.get_recipient fragment api error", message=exc.message)
            raise BadRequest("Unknown error for us from fragment side")

        return StarsRecipient(
            recipient=recipient.found.recipient,
            photo=recipient.found.photo,
            name=recipient.found.name,
        )


stars = StarsService()

import random
from asyncio import sleep

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import FragError, FragRequestValidationError, ResourceNotFound
from src.fragment_transaction.models import FTMetadata
from src.fragment_transaction.service import (
    fragment_transaction as fragment_transaction_service,
)
from src.integrations.fragment import Fragment
from src.integrations.fragment.exceptions import FragmentAPIUsersNotFound
from src.logging import get_logger
from src.models import User
from src.models.fragment_transactions import FragmentTransactionReason
from src.stars.schemas import BuyStars, BuyStarsResponse, StarsRecipient

log = get_logger()


class StarsService:
    async def buy(
        self,
        session: AsyncSession,
        user: User,
        data: BuyStars,
        fragment: Fragment,
    ) -> BuyStarsResponse:
        log.info("Buy stars request", quantity=data.quantity, username=data.username)

        recipient_data = await self.get_recipient(
            fragment=fragment, username=data.username, quantity=data.quantity
        )
        await sleep(0.05)

        if len(data.username) < 3:
            raise FragRequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "username"),
                        "msg": "stars buy request must have a username with lenght bigger than 3",
                        "input": data.username,
                    }
                ]
            )

        buy_request = await fragment.init_buy_stars_request(
            recipient=recipient_data.recipient, quantity=data.quantity
        )
        await sleep(0.05)

        buy_link = await fragment.get_buy_stars_link(
            req_id=buy_request.req_id, show_sender=False
        )

        if buy_link.ok is False:
            raise FragError("Buy link that we recieved is invalid")

        tc_transaction = buy_link.transaction

        fragment_transaction = await fragment_transaction_service.send_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=FragmentTransactionReason.stars,
            metadata=FTMetadata(
                recipient=recipient_data.recipient,
                recipient_username=data.username,
                stars_amount=data.quantity,
            ),
        )

        return BuyStarsResponse(
            message_hash=fragment_transaction.transaction.message_hash,
            transaction_id=fragment_transaction.id,
            photo=recipient_data.photo,
            name=recipient_data.name,
            amount=fragment_transaction.amount,
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
        except FragmentAPIUsersNotFound:
            raise ResourceNotFound("User is not found")

        return StarsRecipient(
            recipient=recipient.found.recipient,
            photo=recipient.found.photo,
            name=recipient.found.name,
        )


stars = StarsService()

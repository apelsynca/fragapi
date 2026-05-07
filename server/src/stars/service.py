import random

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BadRequest, ResourceNotFound
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.rest import FragmentRest
from src.logging import get_logger
from src.models import TransactionReason, User
from src.payment.service import payment as payment_service
from src.stars.schemas import BuyStarsResponse, StarsRecipient
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction

log = get_logger()


class StarsService:
    async def buy_from_tc_transaction(
        self,
        session: AsyncSession,
        user: User,
        wallet_manager: WalletManager,
        transaction: TonConnectTransaction,
    ) -> BuyStarsResponse:
        log.debug("Buying stars from TC transaction", user=user)
        message_hash = await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            transaction=transaction,
            reason=TransactionReason.STARS,
        )

        return BuyStarsResponse(message_hash=message_hash)

    async def get_tc_transaction(
        self, fragment_rest: FragmentRest, username: str, quantity: int
    ) -> TonConnectTransaction:
        if quantity < 50 or quantity > 10_000_000:
            raise BadRequest("Invalid quantity")

        recipient_data = await self.get_recipient(
            fragment_rest, username=username, quantity=quantity
        )

        buy_request = await fragment_rest.init_buy_stars_request(
            recipient=recipient_data.recipient, quantity=quantity
        )

        buy_link = await fragment_rest.get_buy_stars_link(
            req_id=buy_request.req_id, show_sender=False
        )

        return buy_link.transaction

    async def get_recipient(
        self, fragment_rest: FragmentRest, username: str, *, quantity: int | None = None
    ) -> StarsRecipient:
        try:
            recipient = await fragment_rest.search_stars_recipient(
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

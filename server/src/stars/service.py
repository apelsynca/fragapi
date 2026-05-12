import random

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BadRequest, ResourceNotFound
from src.fragment import Fragment
from src.fragment.exceptions import FragmentAPIUsersNotFound
from src.logging import get_logger
from src.models import TransactionReason, User
from src.payments.service import payment as payment_service
from src.stars.schemas import BuyStars, BuyStarsResponse, StarsRecipient
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction

log = get_logger()


class StarsService:
    async def buy(
        self,
        session: AsyncSession,
        user: User,
        data: BuyStars,
        fragment: Fragment,
        wallet_manager: WalletManager,
    ) -> BuyStarsResponse:
        log.info("Buy stars request", quantity=data.quantity, username=data.username)

        recipient_data = await self.get_recipient(
            fragment_rest=fragment_rest, username=data.username, quantity=data.quantity
        )
        transaction = await self.get_tc_transaction(
            fragment_rest, recipient_data=recipient_data, quantity=data.quantity
        )

        return await self.buy_from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=transaction,
            recipient=recipient_data.recipient,
        )

    async def buy_from_tc_transaction(
        self,
        session: AsyncSession,
        user: User,
        wallet_manager: WalletManager,
        tc_transaction: TonConnectTransaction,
        recipient: str,
    ) -> BuyStarsResponse:
        log.debug("Buying stars from TC transaction", user=user)
        message_hash = await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=tc_transaction,
            reason=TransactionReason.STARS,
            recipient=recipient,
        )

        return BuyStarsResponse(message_hash=message_hash)

    async def get_tc_transaction(
        self, fragment: Fragment, recipient_data: StarsRecipient, quantity: int
    ) -> TonConnectTransaction:
        if quantity < 50 or quantity > 10_000_000:
            raise BadRequest("Invalid quantity")

        buy_request = await fragment_rest.init_buy_stars_request(
            recipient=recipient_data.recipient, quantity=quantity
        )

        buy_link = await fragment_rest.get_buy_stars_link(
            req_id=buy_request.req_id, show_sender=False
        )

        return buy_link.transaction

    async def get_recipient(
        self, fragment: Fragment, username: str, *, quantity: int | None = None
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

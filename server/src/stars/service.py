import random

from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import to_amount

from src.exceptions import BadRequest, FragError, InsuficcientFunds, ResourceNotFound
from src.fee import after_fee, after_ton_network_fee
from src.fragment import Fragment
from src.fragment.exceptions import FragmentAPIUsersNotFound
from src.fragment_transaction.service import (
    fragment_transaction as fragment_transaction_service,
)
from src.logging import get_logger
from src.models import User
from src.stars.schemas import BuyStars, BuyStarsResponse, StarsRecipient
from src.users.repository import UserRepository
from src.wallet.manager import WalletManager, WalletManagerError
from src.wallet.service import wallet as wallet_service
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
            fragment=fragment, username=data.username, quantity=data.quantity
        )
        transaction = await self._get_tc_transaction(
            fragment, recipient_data=recipient_data, quantity=data.quantity
        )

        return await self.buy_from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=transaction,
            recipient=recipient_data.recipient,
            username=data.username,
        )

    async def _get_tc_transaction(
        self, fragment: Fragment, recipient_data: StarsRecipient, quantity: int
    ) -> TonConnectTransaction:
        if quantity < 50 or quantity > 10_000_000:
            raise BadRequest("Invalid quantity")

        buy_request = await fragment.init_buy_stars_request(
            recipient=recipient_data.recipient, quantity=quantity
        )

        buy_link = await fragment.get_buy_stars_link(
            req_id=buy_request.req_id, show_sender=False
        )

        return buy_link.transaction

    async def buy_from_tc_transaction(
        self,
        session: AsyncSession,
        user: User,
        wallet_manager: WalletManager,
        tc_transaction: TonConnectTransaction,
        recipient: str,
        username: str,
    ) -> BuyStarsResponse:
        log.debug("Buying stars from TC transaction", user=user)

        user_repository = UserRepository.from_session(session)
        await user_repository.get_by_id_for_update(id=user.id)

        amount_from_transaction = float(to_amount(tc_transaction.messages[0].amount))
        with_fee_amount = after_fee(after_ton_network_fee(amount_from_transaction))

        if with_fee_amount >= user.balance:
            raise InsuficcientFunds()

        user.balance -= with_fee_amount

        try:
            transaction = await wallet_service.send_from_tc_transaction(
                session=session,
                wallet_manager=wallet_manager,
                tc_transaction=tc_transaction,
            )
        except WalletManagerError:  # bad
            raise FragError("We dont have money")

        await fragment_transaction_service.create_stars(
            session=session,
            user=user,
            amount=0,
            recipient=recipient,
            username=username,
            transaction=transaction,
        )

        assert transaction.message_hash

        return BuyStarsResponse(message_hash=transaction.message_hash)

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

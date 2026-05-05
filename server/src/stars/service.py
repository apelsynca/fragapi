import random

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BadRequest, FragError, InsuficcientFunds, ResourceNotFound
from src.fee import after_fee, after_ton_network_fee
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.rest import FragmentRest
from src.logging import get_logger
from src.models.transactions import TransactionReason, TransactionStatus
from src.stars.schemas import BuyStarsResponse, StarsRecipient
from src.transactions.service import transaction as transaction_service
from src.users.repository import UserRepository
from src.wallet.service import wallet as wallet_service

log = get_logger()


class StarsService:
    async def buy(
        self,
        session: AsyncSession,
        fragment_rest: FragmentRest,
        user_id: int,
        username: str,
        quantity: int,
    ) -> BuyStarsResponse:
        if quantity < 50 or quantity > 10_000_000:
            raise BadRequest("Invalid quantity")

        recipient_data = await self.get_recipient(fragment_rest, username=username)

        buy_request = await fragment_rest.init_buy_stars_request(
            recipient=recipient_data.recipient, quantity=quantity
        )
        stars_price = after_ton_network_fee(after_fee(buy_request.amount))

        log.info(
            "stars_service.buy",
            from_user_id=user_id,
            username=username,
            quantity=quantity,
            stars_price=stars_price,
        )

        user = await UserRepository.from_session(session).get_by_id_for_update(
            id=user_id
        )
        if user is None:
            raise FragError()

        if stars_price > user.balance:
            raise InsuficcientFunds("Not enough balance")

        user.balance = user.balance - stars_price

        wallet_balance = await wallet_service.get_balance()
        if wallet_balance < stars_price:
            raise FragError()

        # NOTE: maybe here would be a great idea to send it to taskiq
        buy_link = await fragment_rest.get_buy_stars_link(
            req_id=buy_request.req_id, show_sender=False
        )

        transaction = await transaction_service.create(
            session=session,
            amount=stars_price,
            reason=TransactionReason.STARS,
            user=user,
            recipient=username,
            status=TransactionStatus.PENDING,
        )

        try:
            message_hash = await wallet_service.transfer_from_tc(
                transaction=buy_link.transaction
            )
        except Exception:
            transaction.status = TransactionStatus.FAILED
            log.error("stars_service.buy transfering error")
            raise

        transaction.message_hash = message_hash

        return BuyStarsResponse(message_hash=message_hash)

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

    async def get_single_star_price(self) -> float:
        return 0

    async def get_price(self, quantity: int):
        if quantity < 50 or quantity > 10_000_000:
            raise BadRequest("Invalid quantity")


stars = StarsService()

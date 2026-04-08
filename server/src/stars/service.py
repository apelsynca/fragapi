import re

from src.config import settings
from src.exceptions import AppError, InsuficcientFunds, ResourceNotFound
from src.fragment import fragment
from src.fragment.exceptions import FragmentBadRequest
from src.kit.utils import after_fee
from src.logging import get_logger
from src.models import TransactionReason, TransactionStatus, User
from src.ton_wallet import wallet
from src.transactions.service import TransactionService
from src.users.service import UserService

from .schemas import StarsRecipient

log = get_logger()


class StarsService:
    USD_STAR_PRICE = 0.015

    async def buy(
        self,
        user_service: UserService,
        transaction_service: TransactionService,
        user: User,
        quantity: int,
        username: str,
    ) -> str:
        log.info(
            "Buy stars request",
            user=user,
            username=username,
            quantity=quantity,
        )

        if quantity < 50:
            raise ValueError("Stars amount should be bigger than 50")

        recipient_data = await fragment.search_stars_recipient(
            query=username, quantity=quantity
        )

        buy_stars_request = await fragment.init_buy_stars_request(
            recipient=recipient_data.found.recipient, quantity=quantity
        )

        stars_ton_price = after_fee(buy_stars_request.amount)
        user_stars_ton_price = stars_ton_price * (1 + settings.price_markup)
        if user.balance < user_stars_ton_price:
            raise InsuficcientFunds

        balance = await wallet.get_real_ton_balance()
        if balance < stars_ton_price:
            raise AppError(f"We have insufficcient funds: {balance}")

        link = await fragment.get_buy_stars_link(req_id=buy_stars_request.req_id)

        await user_service.update_balance(
            user=user, new_balance=user.balance - user_stars_ton_price
        )

        # Create transaction with PENDING status first
        transaction = await transaction_service.create(
            amount=user_stars_ton_price,
            reason=TransactionReason.STARS,
            user=user,
            stars_quantity=quantity,
            recipient=username,
            status=TransactionStatus.PENDING,
        )

        try:
            tx_hash = await wallet.transfer_from_tc(
                message=link.transaction.messages[0],
                valid_until=link.transaction.valid_until,
            )

            # Update transaction with tx_hash and COMPLETED status
            await transaction_service.update_status(
                transaction=transaction,
                status=TransactionStatus.COMPLETED,
                tx_hash=tx_hash,
            )

            log.info(
                "New buy stars transaction!",
                hash=tx_hash,
                username=username,
                quantity=quantity,
                transaction_id=transaction.id,
            )

            return tx_hash

        except Exception as exc:
            # If transfer fails, mark transaction as FAILED
            await transaction_service.update_status(
                transaction=transaction,
                status=TransactionStatus.FAILED,
            )
            log.error(
                "Failed to transfer stars",
                error=str(exc),
                username=username,
                quantity=quantity,
                transaction_id=transaction.id,
            )
            raise

    async def get_recipient(self, username: str) -> StarsRecipient:
        try:
            recipient_data = await fragment.search_stars_recipient(query=username)
        except FragmentBadRequest:
            raise ResourceNotFound(f"No recipient found by username {username}")

        photo_match = re.search(r'src="(.*)"', recipient_data.found.photo)

        return StarsRecipient(
            recipient=recipient_data.found.recipient,
            name=recipient_data.found.name,
            photo=photo_match.group(1) if photo_match else None,
        )


stars_service = StarsService()

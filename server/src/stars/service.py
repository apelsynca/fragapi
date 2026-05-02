import re
from time import time

from pydantic import ValidationError

from src.config import settings
from src.exceptions import AppError, InsuficcientFunds, ResourceNotFound
from src.fragment_rest.exceptions import FragmentBadRequest, FragmentUserNotFound
from src.fragment_rest.main import FragmentRest
from src.kit.utils import after_fee
from src.logging import get_logger
from src.models import TransactionReason, TransactionStatus, User
from src.stars.schemas import StarsRecipient
from src.transactions.service import transaction as transaction_service
from src.wallet.service import wallet as wallet_service

log = get_logger()


class StarsService:
    CACHE_TIME = 60

    def __init__(self) -> None:
        self.last_price = None
        self.price_ut = 0

    async def buy(
        self,
        fragment_rest: FragmentRest,
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
            raise ValidationError("Stars amount should be bigger than 50")

        try:
            recipient_data = await fragment_rest.search_stars_recipient(
                query=username, quantity=quantity
            )
        except FragmentUserNotFound:
            raise ResourceNotFound("User not found")

        buy_stars_request = await fragment_rest.init_buy_stars_request(
            recipient=recipient_data.found.recipient, quantity=quantity
        )

        stars_ton_price = after_fee(buy_stars_request.amount)
        user_stars_ton_price = stars_ton_price * (1 + settings.API_PRICE_MARKUP)
        if user.balance < user_stars_ton_price:
            raise InsuficcientFunds

        balance = await wallet_service.get_real_ton_balance()
        if balance < stars_ton_price:
            raise AppError(f"We have insufficcient funds: {balance}")

        link = await fragment_rest.get_buy_stars_link(req_id=buy_stars_request.req_id)

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
            tx_hash = await wallet_service.transfer_from_tc(
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

    async def get_price(self) -> float:
        """
        Returns price in TON's for 1 star.
        """

        now = time()
        if self.last_price is not None and now - self.price_ut < self.CACHE_TIME:
            return self.last_price

        recipient_data = await fragment.search_stars_recipient(
            query="apelsynca", quantity=100
        )
        buy_stars_request = await fragment.init_buy_stars_request(
            recipient=recipient_data.found.recipient, quantity=100
        )

        self.last_price = buy_stars_request.amount / 100
        self.price_ut = now

        return self.last_price


stars = StarsService()

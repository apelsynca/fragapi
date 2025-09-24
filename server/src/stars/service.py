import re

from src.config import settings
from src.exceptions import BadRequest, InsuficcientFunds, ResourceNotFound
from src.fragment import fragment
from src.fragment.exceptions import FragmentBadRequest
from src.kit.utils import after_fee
from src.logging import get_logger
from src.models import TransactionReason, User
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
        show_sender: bool = False,
    ) -> str:
        log.info(
            "Buy stars request",
            user=user,
            username=username,
            quantity=quantity,
            show_sender=show_sender,
        )

        if quantity < 50:
            raise ValueError("Stars amount should be bigger than 50")

        try:
            recipient_data = await fragment.search_stars_recipient(
                query=username, quantity=quantity
            )
        except FragmentBadRequest as exc:
            raise BadRequest(str(exc))

        buy_stars_request = await fragment.init_buy_stars_request(
            recipient=recipient_data.found.recipient, quantity=quantity
        )

        stars_ton_price = after_fee(buy_stars_request.amount)
        user_stars_ton_price = stars_ton_price * (1 + settings.price_markup)
        if user.balance < user_stars_ton_price:
            raise InsuficcientFunds

        balance = await wallet.balance()
        if balance < stars_ton_price:
            raise BadRequest("We have insufficcient funds")

        link = await fragment.get_buy_stars_link(
            req_id=buy_stars_request.req_id, show_sender=show_sender
        )

        await user_service.update_balance(
            user=user, new_balance=user.balance - user_stars_ton_price
        )
        await transaction_service.create(
            amount=user_stars_ton_price, reason=TransactionReason.STARS, user=user
        )

        tx_hash = await wallet.transfer_from_tc(
            message=link.transaction.messages[0],
            valid_until=link.transaction.valid_until,
        )
        log.info(
            "New buy stars transaction!",
            hash=tx_hash,
            username=username,
            quantity=quantity,
        )

        return tx_hash

    async def get_recipient(self, username: str) -> StarsRecipient:
        try:
            recipient_data = await fragment.search_stars_recipient(query=username)
        except FragmentBadRequest:
            raise ResourceNotFound("No recipient found")

        photo_match = re.search(r'src="(.*)"', recipient_data.found.photo)

        return StarsRecipient(
            recipient=recipient_data.found.recipient,
            name=recipient_data.found.name,
            photo=photo_match.group(1) if photo_match else None,
        )


stars_service = StarsService()

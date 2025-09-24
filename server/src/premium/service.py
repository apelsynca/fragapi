import re

from src.config import settings
from src.exceptions import BadRequest, InsuficcientFunds, ResourceNotFound
from src.fragment import fragment
from src.fragment.enums import PremiumMonths
from src.fragment.exceptions import FragmentBadRequest
from src.kit.utils import after_fee
from src.logging import get_logger
from src.models.transactions import TransactionReason
from src.models.users import User
from src.premium.schemas import PremiumRecipient
from src.ton_wallet import wallet
from src.transactions.service import TransactionService
from src.users.service import UserService

log = get_logger()


class PremiumService:
    async def buy(
        self,
        user_service: UserService,
        transaction_service: TransactionService,
        user: User,
        username: str,
        months: PremiumMonths,
        show_sender: bool = False,
    ) -> str:
        try:
            recipient_data = await fragment.search_premium_recipient(
                query=username, months=months
            )
        except FragmentBadRequest as exc:
            raise BadRequest(str(exc))

        buy_premium_request = await fragment.init_premium_request(
            recipient=recipient_data.found.recipient, months=months
        )

        premium_ton_price = after_fee(buy_premium_request.amount)
        user_premium_ton_price = premium_ton_price * (1 + settings.price_markup)
        if user.balance < user_premium_ton_price:
            raise InsuficcientFunds

        balance = await wallet.balance()
        if balance < premium_ton_price:
            raise BadRequest("We have insufficcient funds")

        link = await fragment.get_premium_link(
            req_id=buy_premium_request.req_id, show_sender=show_sender
        )

        await user_service.update_balance(
            user=user, new_balance=user.balance - user_premium_ton_price
        )
        await transaction_service.create(
            amount=user_premium_ton_price, reason=TransactionReason.PREMIUM, user=user
        )

        tx_hash = await wallet.transfer_from_tc(
            message=link.transaction.messages[0],
            valid_until=link.transaction.valid_until,
        )
        log.info(
            "New buy premium transaction!",
            hash=tx_hash,
            username=username,
            months=months,
        )

        return tx_hash

    async def get_recipient(self, username: str) -> PremiumRecipient:
        try:
            recipient_data = await fragment.search_premium_recipient(query=username)
        except FragmentBadRequest:
            raise ResourceNotFound("No recipient found")

        photo_match = re.search(r'src="(.*)"', recipient_data.found.photo)

        return PremiumRecipient(
            recipient=recipient_data.found.recipient,
            name=recipient_data.found.name,
            photo=photo_match.group(1) if photo_match else None,
        )


premium_service = PremiumService()

import re

from src.config import settings
from src.exceptions import AppError, InsuficcientFunds, ResourceNotFound
from src.fragment_rest import fragment_rest
from src.fragment_rest.enums import PremiumMonths
from src.fragment_rest.exceptions import FragmentBadRequest
from src.kit.utils import after_fee
from src.logging import get_logger
from src.models.transactions import TransactionReason, TransactionStatus
from src.models.users import User
from src.premium.schemas import PremiumRecipient
from src.transactions.service import TransactionService
from src.users.service import UserService
from src.wallet.service import wallet as wallet_service

log = get_logger()


class PremiumService:
    async def buy(
        self,
        user_service: UserService,
        transaction_service: TransactionService,
        user: User,
        username: str,
        months: PremiumMonths,
    ) -> str:
        recipient_data = await fragment_rest.search_premium_recipient(
            query=username, months=months
        )

        buy_premium_request = await fragment_rest.init_premium_request(
            recipient=recipient_data.found.recipient, months=months
        )

        premium_ton_price = after_fee(buy_premium_request.amount)
        user_premium_ton_price = premium_ton_price * (1 + settings.API_PRICE_MARKUP)
        if user.balance < user_premium_ton_price:
            raise InsuficcientFunds

        balance = await wallet_service.get_real_ton_balance()
        if balance < premium_ton_price:
            raise AppError(f"We have insufficcient funds: {balance}")

        link = await fragment_rest.get_premium_link(req_id=buy_premium_request.req_id)

        await user_service.update_balance(
            user=user, new_balance=user.balance - user_premium_ton_price
        )

        # Create transaction with PENDING status first
        transaction = await transaction_service.create(
            amount=user_premium_ton_price,
            reason=TransactionReason.PREMIUM,
            user=user,
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
                "New buy premium transaction!",
                hash=tx_hash,
                username=username,
                months=months,
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
                "Failed to transfer premium",
                error=str(exc),
                username=username,
                months=months,
                transaction_id=transaction.id,
            )
            raise

    async def get_recipient(self, username: str) -> PremiumRecipient:
        try:
            recipient_data = await fragment.search_premium_recipient(query=username)
        except FragmentBadRequest:
            raise ResourceNotFound(f"No recipient found by username {username}")

        photo_match = re.search(r'src="(.*)"', recipient_data.found.photo)

        return PremiumRecipient(
            recipient=recipient_data.found.recipient,
            name=recipient_data.found.name,
            photo=photo_match.group(1) if photo_match else None,
        )


premium_service = PremiumService()

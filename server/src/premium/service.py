from sqlalchemy.ext.asyncio import AsyncSession

from src.enums import PremiumMonths
from src.exceptions import ResourceNotFound
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.rest import FragmentRest
from src.logging import get_logger
from src.models import TransactionReason, User
from src.payment.service import payment as payment_service
from src.premium.schemas import BuyPremiumResponse, PremiumRecipient
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction

log = get_logger()


class PremiumService:
    async def gift_from_tc_transaction(
        self,
        session: AsyncSession,
        user: User,
        wallet_manager: WalletManager,
        transaction: TonConnectTransaction,
    ) -> BuyPremiumResponse:
        log.info("HELLO IM HERE")
        message_hash = await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            transaction=transaction,
            reason=TransactionReason.PREMIUM,
        )

        return BuyPremiumResponse(message_hash=message_hash)

    async def get_buy_tc_transaction(
        self, fragment_rest: FragmentRest, username: str, months: PremiumMonths
    ) -> TonConnectTransaction:
        recipient_data = await self.get_recipient(
            fragment_rest=fragment_rest, username=username, months=months
        )

        buy_request = await fragment_rest.init_gift_premium_request(
            recipient=recipient_data.recipient, months=months.value
        )
        buy_link = await fragment_rest.get_gift_premium_link(req_id=buy_request.req_id)

        return buy_link.transaction

    async def get_recipient(
        self,
        fragment_rest: FragmentRest,
        username: str,
        *,
        months: PremiumMonths = PremiumMonths.YEAR,
    ) -> PremiumRecipient:
        try:
            recipient = await fragment_rest.search_premium_gift_recipient(
                query=username, months=months.value
            )
        except FragmentAPIUsersNotFound:
            raise ResourceNotFound("User is not found")

        return PremiumRecipient(
            recipient=recipient.found.recipient,
            photo=recipient.found.photo,
            name=recipient.found.name,
        )


premium = PremiumService()

from sqlalchemy.ext.asyncio import AsyncSession

from src.enums import PremiumMonths
from src.exceptions import ResourceNotFound
from src.fragment import Fragment
from src.fragment.exceptions import FragmentAPIUsersNotFound
from src.logging import get_logger
from src.models import TransactionReason, User
from src.payments.service import payment as payment_service
from src.premium.schemas import BuyPremium, BuyPremiumResponse, PremiumRecipient
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction

log = get_logger()


class PremiumService:
    async def buy(
        self,
        session: AsyncSession,
        user: User,
        data: BuyPremium,
        fragment: Fragment,
        wallet_manager: WalletManager,
    ) -> BuyPremiumResponse:
        log.info("Buying premium", months=data.months, username=data.username)

        recipient_data = await self.get_recipient(
            fragment, username=data.username, months=data.months
        )

        transaction = await self.get_buy_tc_transaction(
            fragment=fragment,
            recipient_data=recipient_data,
            months=data.months,
        )

        return await self.gift_from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=transaction,
            recipient=recipient_data.recipient,
        )

    async def gift_from_tc_transaction(
        self,
        session: AsyncSession,
        user: User,
        wallet_manager: WalletManager,
        tc_transaction: TonConnectTransaction,
        recipient: str,
    ) -> BuyPremiumResponse:
        log.debug("Buying premium from TC transaction", user=user)
        message_hash = await payment_service.from_tc_transaction(
            session=session,
            user=user,
            wallet_manager=wallet_manager,
            tc_transaction=tc_transaction,
            recipient=recipient,
            reason=TransactionReason.PREMIUM,
        )

        return BuyPremiumResponse(message_hash=message_hash)

    async def get_buy_tc_transaction(
        self,
        fragment: Fragment,
        recipient_data: PremiumRecipient,
        months: PremiumMonths,
    ) -> TonConnectTransaction:
        buy_request = await fragment.init_gift_premium_request(
            recipient=recipient_data.recipient, months=months.value
        )
        buy_link = await fragment.get_gift_premium_link(req_id=buy_request.req_id)

        return buy_link.transaction

    async def get_recipient(
        self,
        fragment: Fragment,
        username: str,
        *,
        months: PremiumMonths = PremiumMonths.YEAR,
    ) -> PremiumRecipient:
        try:
            recipient = await fragment.search_premium_gift_recipient(
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

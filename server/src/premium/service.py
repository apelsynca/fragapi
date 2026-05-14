from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import to_amount

from src.enums import PremiumMonths
from src.exceptions import FragError, InsuficcientFunds, ResourceNotFound
from src.fee import after_fee, after_ton_network_fee
from src.fragment_transaction.service import (
    fragment_transaction as fragment_transaction_service,
)
from src.integrations.fragment import Fragment
from src.integrations.fragment.exceptions import FragmentAPIUsersNotFound
from src.logging import get_logger
from src.models import User
from src.models.fragment_transactions import FragmentTransactionReason
from src.premium.schemas import BuyPremium, BuyPremiumResponse, PremiumRecipient
from src.wallet.manager import WalletManager, WalletManagerError
from src.wallet.service import wallet as wallet_service
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
            username=data.username,
        )

    async def gift_from_tc_transaction(
        self,
        session: AsyncSession,
        user: User,
        wallet_manager: WalletManager,
        tc_transaction: TonConnectTransaction,
        recipient: str,
        username: str,
    ) -> BuyPremiumResponse:
        log.debug("Buying premium from TC transaction", user=user)

        await session.refresh(user, with_for_update=True)

        amount_from_transaction = float(to_amount(tc_transaction.messages[0].amount))
        with_fee_amount = after_fee(after_ton_network_fee(amount_from_transaction))

        if with_fee_amount >= user.balance:
            raise InsuficcientFunds()

        user.balance -= with_fee_amount

        await session.commit()

        try:
            transaction = await wallet_service.send_from_tc_transaction(
                session=session,
                wallet_manager=wallet_manager,
                tc_transaction=tc_transaction,
            )
        except WalletManagerError:  # bad
            raise FragError("We dont have money")

        await fragment_transaction_service.create(
            session=session,
            user=user,
            amount=with_fee_amount,
            recipient=recipient,
            username=username,
            transaction=transaction,
            reason=FragmentTransactionReason.premium,
        )

        assert transaction.message_hash

        return BuyPremiumResponse(message_hash=transaction.message_hash)

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

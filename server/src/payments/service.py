import base64
from secrets import token_urlsafe

from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import begin_cell, to_amount, to_nano

from src.config import settings
from src.exceptions import (
    BadRequest,
    FragError,
    FragRequestValidationError,
    InsuficcientFunds,
    ResourceNotFound,
)
from src.fee import TON_FEE, after_fee, after_ton_network_fee
from src.kit.ton_connect import TonConnectMessage
from src.logging import get_logger
from src.models import Payment, User
from src.models.transactions import TransactionReason
from src.payments.repository import PaymentRepository
from src.transactions.service import transaction as transaction_service
from src.users.repository import UserRepository
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction

log = get_logger()


class PaymentService:
    COMMENT_TEMPLATE = "FragAPI top-up\n\nRef#{}"

    async def ton_payment_request(
        self, session: AsyncSession, user: User, amount: float
    ) -> TonConnectMessage:
        if amount < settings.MIN_DEPOSIT_AMOUNT:
            raise BadRequest()

        payment = await self.create(session=session, user=user, amount=amount)

        payload_cell = (
            begin_cell()
            .store_uint(0, 32)
            .store_snake_string(self.COMMENT_TEMPLATE.format(payment.hash))
            .end_cell()
        )
        payload_boc = payload_cell.to_boc()
        payload = base64.b64encode(payload_boc).decode("utf-8")

        return TonConnectMessage(
            address=settings.TON_ADDRESS,
            amount=to_nano(payment.amount),
            payload=payload,
        )

    async def create(self, session: AsyncSession, user: User, amount: float) -> Payment:
        repository = PaymentRepository.from_session(session)

        return await repository.create(
            Payment(user=user, amount=amount, hash=token_urlsafe(24)), flush=True
        )

    async def process_ton_payment(self, session: AsyncSession, hash: str) -> None:
        repository = PaymentRepository.from_session(session)

        payment = await repository.get_by_hash(hash=hash)
        if payment is None:
            raise ResourceNotFound()

        log.info("User balance top-up", amount=payment.amount, user=payment.user)

        payment.user.balance += payment.amount

    async def from_tc_transaction(
        self,
        session: AsyncSession,
        user: User,
        wallet_manager: WalletManager,
        tc_transaction: TonConnectTransaction,
        recipient: str,
        reason: TransactionReason,
    ) -> str:
        if len(tc_transaction.messages) != 1:
            raise FragRequestValidationError(
                [
                    {
                        "loc": ("transaction", "messages"),
                        "msg": "only one transaction message is required",
                        "type": "value_error",
                        "input": f"given {len(tc_transaction.messages)}",
                    }
                ]
            )

        if tc_transaction.messages[0].payload is None:
            raise FragRequestValidationError(
                [
                    {
                        "loc": ("transaction", "message", "payload"),
                        "msg": "transaction message must have a payload",
                        "type": "value_error",
                        "input": None,
                    }
                ]
            )

        amount_from_transaction = float(to_amount(tc_transaction.messages[0].amount))
        with_fee_amount = after_fee(after_ton_network_fee(amount_from_transaction))

        wallet_balance = await wallet_manager.get_balance()
        # 0.05 is what would be left on the wallet and still raises
        if wallet_balance - 0.05 < amount_from_transaction + TON_FEE:
            raise FragError("FragAPI internal wallet balance is too low!")

        user_repository = UserRepository.from_session(session)
        # WARN: im not sure whether it is not HACKABLE!!!!
        await user_repository.get_by_id_for_update(id=user.id)

        if with_fee_amount >= user.balance:
            raise InsuficcientFunds()

        user.balance -= with_fee_amount

        await transaction_service.create(
            session=session,
            amount=with_fee_amount,
            reason=reason,
            user=user,
            recipient=recipient,
            message_hash=None,
        )

        return await wallet_manager.transfer_from_tc(transaction=tc_transaction)


payment = PaymentService()

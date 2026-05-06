from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import to_amount

from src.exceptions import FragError, FragRequestValidationError, InsuficcientFunds
from src.fee import TON_FEE, after_fee, after_ton_network_fee
from src.models import User
from src.models.transactions import TransactionReason
from src.users.repository import UserRepository
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction


class PaymentService:
    async def from_tc_transaction(
        self,
        session: AsyncSession,
        user: User,
        wallet_manager: WalletManager,
        transaction: TonConnectTransaction,
        reason: TransactionReason,
    ) -> str:
        if len(transaction.messages) != 1:
            raise FragRequestValidationError(
                [
                    {
                        "loc": ("transaction", "messages"),
                        "msg": "only one transaction message is required",
                        "type": "value_error",
                        "input": None,
                    }
                ]
            )

        if transaction.messages[0].payload is None:
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

        amount_from_transaction = float(to_amount(transaction.messages[0].amount))
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

        return await wallet_manager.transfer_from_tc(transaction=transaction)


payment = PaymentService()

from src.exceptions import FragRequestValidationError
from src.postgres import AsyncSession
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction


class WalletService:
    async def send_from_tc_transaction(
        self,
        session: AsyncSession,
        wallet_manager: WalletManager,
        tc_transaction: TonConnectTransaction,
    ) -> str:
        """
        Validate that message is right
        Create pending transaction in db

        """

        if len(tc_transaction.messages) != 1:
            raise FragRequestValidationError(
                [
                    {
                        "loc": ("transaction", "messages"),
                        "msg": "only one transaction message is required",
                        "type": "value_error",
                        "input": len(tc_transaction.messages),
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
                        "input": tc_transaction.messages[0].payload,
                    }
                ]
            )

        wallet = await wallet_manager.get_wallet_for_amount(amount=0)

        return ""


wallet = WalletService()

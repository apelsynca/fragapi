from ton_core import Address, Cell, WalletV5Params
from tonutils.contracts import ExternalMessage

from src.exceptions import FragRequestValidationError
from src.integrations.ton_wallet.manager import WalletManager
from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction


class WalletService:
    async def send_from_tc_transaction(
        self,
        wallet_manager: WalletManager,
        tc_transaction: TonConnectTransaction,
    ) -> ExternalMessage:
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

        message = tc_transaction.messages[0]
        wallet = await wallet_manager.get_wallet_for_amount(amount=message.amount)

        body = self.extract_body(message=message)
        valid_until = int(tc_transaction.valid_until.timestamp()) + 10

        return await wallet.transfer(
            destination=Address(message.address),
            body=body,
            amount=message.amount,
            params=WalletV5Params(valid_until=valid_until),
        )

    def extract_body(self, message: TonConnectMessage) -> Cell:
        if message.payload is None:
            raise RuntimeError("Omg shiiit")

        padded_payload = message.payload + "=" * (-len(message.payload) % 4)
        return Cell.one_from_boc(padded_payload)


wallet = WalletService()

from datetime import datetime

from pytoniq_core import Address, Cell, Slice, Transaction
from tonutils.client import TonapiClient
from tonutils.wallet import WalletV5R1 as _Wallet

from src.config import settings
from src.ton_connect.types import TonConnectMessage


class Wallet(_Wallet):
    async def transfer_from_tc(
        self, message: TonConnectMessage, valid_until: datetime
    ) -> str:
        body = None

        if message.payload:
            padded_payload = message.payload + "=" * (
                ((4 - len(message.payload)) % 4) % 4
            )
            body = Cell.one_from_boc(padded_payload)

        return await self.raw_transfer(
            messages=[
                self.create_wallet_internal_message(
                    destination=Address(message.address),
                    value=message.amount,
                    body=body,
                ),
            ],
            valid_until=int(valid_until.timestamp()),
        )


class MyTonAPIClient(TonapiClient):
    async def get_transaction(self, hash: str) -> Transaction:
        method = f"/blockchain/transactions/{hash}"
        result = await self._get(method=method)

        cell_slice = Slice.one_from_boc(result.get("raw"))
        return Transaction.deserialize(cell_slice)


tonapi_client = MyTonAPIClient(api_key=settings.ton_api_key.get_secret_value())


def get_wallet() -> Wallet:
    wallet, *_ = Wallet.from_mnemonic(
        client=tonapi_client, mnemonic=settings.get_secret_wallet_mnemonic()
    )
    return wallet  # pyright: ignore


wallet = get_wallet()

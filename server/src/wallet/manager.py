from ton_core import NetworkGlobalID, to_amount
from tonutils.contracts import WalletV5R1

from src.config import settings
from src.kit.ton_connect import TonConnect

if settings.is_production():
    env_network_id = NetworkGlobalID.MAINNET
else:
    env_network_id = NetworkGlobalID.TESTNET


class WalletManagerError(Exception):
    pass


class WalletManager:
    """
    Service of a global FragAPI wallet

    Since the wallets can be split
    """

    def __init__(self, ton_wallets: list[WalletV5R1]) -> None:
        if len(ton_wallets) != 1:
            raise

        self.wallet = ton_wallets[0]

    def get_ton_connect(self, tc_domain: str) -> TonConnect:
        return TonConnect(self.wallet, tc_domain=tc_domain)

    async def get_balance(self) -> int:
        await self.wallet.refresh()
        return self.wallet.balance

    # async def transfer_from_tc(self, transaction: TonConnectTransaction) -> str:
    #     message = transaction.messages[0]
    #     address = Address(message.address)
    #     body = None
    #
    #     if message.payload is not None:
    #         padded_payload = message.payload + "=" * (
    #             ((4 - len(message.payload)) % 4) % 4
    #         )
    #         body = Cell.one_from_boc(padded_payload)
    #
    #     valid_until = int(transaction.valid_until.timestamp()) + 10
    #
    #     ext_msg = await self.wallet.transfer(
    #         destination=address,
    #         amount=message.amount,
    #         body=body,
    #         params=WalletV5Params(valid_until=valid_until),
    #     )
    #
    #     return ext_msg.normalized_hash

    async def get_wallet_for_amount(self, amount: float) -> WalletV5R1:
        selected_wallet = self.wallet

        await selected_wallet.refresh()
        if to_amount(selected_wallet.balance) <= amount:
            raise WalletManagerError()

        return selected_wallet

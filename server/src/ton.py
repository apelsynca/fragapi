from fastapi import Request
from ton_core import NetworkGlobalID
from tonutils.clients import ToncenterClient
from tonutils.contracts import WalletV5R1

from src.config import Environment, settings

# i know that in development it is bad, but we need to test fragment
network = (
    NetworkGlobalID.MAINNET
    if settings.is_environment({Environment.production, Environment.development})
    else NetworkGlobalID.TESTNET
)

toncenter = ToncenterClient(network=network, api_key=settings.TONCENTER_API_KEY)


def create_wallet():
    wallet, *_ = WalletV5R1.from_mnemonic(
        client=toncenter,  # pyright: ignore
        mnemonic=settings.WALLET_MNEMONIC,
    )
    return wallet


def get_wallet(request: Request) -> WalletV5R1:
    return request.state.wallet

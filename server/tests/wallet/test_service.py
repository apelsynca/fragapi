import random
from datetime import datetime
from unittest.mock import ANY, MagicMock

import pytest
from ton_core import Address, WalletV5Params

from src.exceptions import BadRequest, FragError
from src.wallet.service import wallet as wallet_service
from src.wallet.types import TonConnectMessage, TonConnectTransaction
from tests.fixtures.random_objects import rstr

random_valid_addresses = [
    "UQDhirptnBk0D904yhJb1dfT9rakVJvsS8J0A-t3JOCI3q4d",
    "UQAACFr-aI2L7qUQPDvFdmj06HtQ0BlM8IMqYCGr5EbvHsz7",
    "UQDaEl25FhUVIJ8RSiJqncKh76OiI3UhtP2g4e-OkHJJYhe-",
]


def generate_fake_ton_connect_transaction(
    payload: str | None = None,
) -> TonConnectTransaction:
    return TonConnectTransaction(
        valid_until=datetime(year=2010, month=10, day=3),
        from_address=random.choice(random_valid_addresses),
        messages=[
            TonConnectMessage(
                address=random.choice(random_valid_addresses), amount=5, payload=payload
            )
        ],
    )


@pytest.mark.asyncio
async def test_raises_if_more_than_one_message(wallet: MagicMock) -> None:
    ton_connect_transaction = generate_fake_ton_connect_transaction(payload="ABC")
    ton_connect_transaction.messages.append(
        TonConnectMessage(
            address=rstr("abc"), amount=random.randint(1, 99), payload=None
        )
    )

    with pytest.raises(FragError):
        await wallet_service.transfer_from_tc(wallet, ton_connect_transaction)


@pytest.mark.asyncio
async def test_calls_wallet_transfer_with_right_data(wallet: MagicMock) -> None:
    transaction = TonConnectTransaction(
        valid_until=datetime(year=2010, month=10, day=3),
        from_address=random.choice(random_valid_addresses),
        messages=[
            TonConnectMessage(
                address="UQAACFr-aI2L7qUQPDvFdmj06HtQ0BlM8IMqYCGr5EbvHsz7",
                amount=5,
                payload=None,
            )
        ],
    )

    await wallet_service.transfer_from_tc(wallet, transaction)

    wallet.transfer.assert_called_once_with(
        destination=Address("UQAACFr-aI2L7qUQPDvFdmj06HtQ0BlM8IMqYCGr5EbvHsz7"),
        amount=ANY,
        body=None,
        params=WalletV5Params(
            valid_until=int(datetime(year=2010, month=10, day=3).timestamp()) + 10
        ),
    )


@pytest.mark.asyncio
async def test_transfer_what_happends_when(wallet: MagicMock) -> None:
    transaction = generate_fake_ton_connect_transaction(payload="somebrokenpayload")

    with pytest.raises(BadRequest):
        await wallet_service.transfer_from_tc(wallet, transaction)

import random

import pytest
from ton_core import to_nano

from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction
from tests.fixtures.random_objects import RANDOM_TON_ADDRESSES, get_tc_transaction


@pytest.fixture
def tc_transaction() -> TonConnectTransaction:
    return get_tc_transaction(
        messages=[
            TonConnectMessage(
                address=random.choice(RANDOM_TON_ADDRESSES),
                amount=to_nano(5.25),
                payload="te6ccgEBAQEAJwAASgAAAAA1MCBUZWxlZ3JhbSBTdGFycyAKClJlZiN4Z01NbTM3bVY",
            )
        ]
    )

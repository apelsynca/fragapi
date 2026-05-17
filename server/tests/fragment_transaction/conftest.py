import pytest
from ton_core import to_nano

from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction
from tests.fixtures.random_objects import get_tc_transaction


@pytest.fixture
def valid_tc_transaction() -> TonConnectTransaction:
    return get_tc_transaction(
        messages=[
            TonConnectMessage(
                address="UQANtyTiJuWgo5cTdrVlzpTzhYD3Heg3ssPoeAW2dM2v6nR1",
                amount=to_nano(5.25),
                payload="te6ccgEBAQEAJwAASgAAAAA1MCBUZWxlZ3JhbSBTdGFycyAKClJlZiN4Z01NbTM3bVY",
            )
        ]
    )


@pytest.fixture
def valid_tc_transaction_hash() -> str:
    return "04ab7405a2e4e5f6fd301505900598570737ec77fbeeeafea641bab5f0ef33eb"

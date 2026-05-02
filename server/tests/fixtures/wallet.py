from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from tonutils.contracts import WalletV5R1


@pytest.fixture(autouse=True)
def wallet(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.ton.get_wallet", spec=WalletV5R1)

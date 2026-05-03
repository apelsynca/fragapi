from unittest.mock import MagicMock

import pytest

from src.kit.ton_connect import TonConnect


@pytest.fixture(autouse=True)
def ton_connect() -> MagicMock:
    ton_connect_mock = MagicMock(spec=TonConnect)

    ton_connect_mock.tc_domain = "fragment.com"

    return ton_connect_mock

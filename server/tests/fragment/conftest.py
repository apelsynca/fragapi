from unittest.mock import MagicMock

import pytest

from src.kit.ton_connect import TonConnect


@pytest.fixture
def ton_connect() -> MagicMock:
    return MagicMock(spec=TonConnect)

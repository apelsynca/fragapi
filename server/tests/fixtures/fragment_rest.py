from unittest.mock import MagicMock

import pytest

from src.fragment_rest.main import FragmentRest
from src.kit.ton_connect import TonConnect


@pytest.fixture
def fragment_rest() -> FragmentRest:
    ton_connect = MagicMock(spec=TonConnect)
    return FragmentRest(ton_connect)

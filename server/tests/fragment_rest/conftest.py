from unittest.mock import MagicMock

import pytest

from src.fragment_rest.models import FragmentSession
from src.kit.ton_connect import TonConnect
from tests.fixtures.random_objects import lstr, rstr


@pytest.fixture
def ton_connect() -> MagicMock:
    ton_connect_mock = MagicMock(spec=TonConnect)

    ton_connect_mock.tc_domain = "fragment.com"

    return ton_connect_mock


@pytest.fixture
def fragment_session() -> FragmentSession:
    return FragmentSession(
        hash=lstr("somehash"),
        ton_proof_payload=rstr("somepayload"),
        cookies={},
    )

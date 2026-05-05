from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.fragment_rest.base_rest import BaseFragmentRest
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


@pytest.fixture(autouse=True)
def load_session_patch(mocker: MockerFixture) -> None:
    mocker.patch.object(BaseFragmentRest, "_load_session", return_value=None)

from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from src.fragment_rest.main import FragmentRest
from src.kit.ton_connect import TonConnect


@pytest.fixture
def fragment_rest(mocker: MockerFixture) -> FragmentRest:
    ton_connect = MagicMock(spec=TonConnect)
    fragment_rest = FragmentRest(ton_connect)

    fragment_rest._client = None
    client_mock = MagicMock(spec=AsyncClient)
    mocker.patch.object(fragment_rest, "client", return_value=client_mock)

    return fragment_rest

from unittest.mock import MagicMock

import pytest

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.fragment_rest.rest import FragmentRest
from src.kit.ton_connect import TonConnect


@pytest.fixture
def fragment_api_client() -> MagicMock:
    return MagicMock(spec=FragmentAPIClient)


@pytest.fixture
def fragment_rest_auth() -> MagicMock:
    return MagicMock(spec=FragmentRestAuth)


@pytest.fixture(autouse=True)
def fragment_rest(
    ton_connect: TonConnect,
    fragment_api_client: MagicMock,
    fragment_rest_auth: MagicMock,
) -> FragmentRest:
    fragment_rest = FragmentRest(ton_connect=ton_connect)

    fragment_rest._api = fragment_api_client
    fragment_rest._auth = fragment_rest_auth

    return fragment_rest


# probably in api client
# @pytest.mark.asyncio
# async def test_request_refreshes_session() -> None:
#     pass

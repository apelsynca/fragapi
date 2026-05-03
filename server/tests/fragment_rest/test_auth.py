from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.kit.ton_connect import TonConnect


@pytest.fixture(autouse=True)
def fragment_api_client() -> MagicMock:
    return MagicMock(spec=FragmentAPIClient)


@pytest.fixture
def fragment_auth_service(
    mocker: MockerFixture,
    fragment_api_client: FragmentAPIClient,
    ton_connect: TonConnect,
) -> FragmentRestAuth:
    mocker.patch.object(FragmentRestAuth, "load_session", return_value=None)

    return FragmentRestAuth(api_client=fragment_api_client, ton_connect=ton_connect)


@pytest.mark.asyncio
async def abcdef() -> None:
    pass

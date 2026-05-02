from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from src.fragment_rest import fragment_rest
from src.fragment_rest.exceptions import FragmentUsersNotFound


@pytest.fixture(autouse=True)
def fragment_client_mock(mocker: MockerFixture) -> MagicMock:
    mocker.patch("src.fragment_rest.fragment_rest.load_session", return_value=None)
    return mocker.patch("src.fragment_rest.fragment_rest.client", spec=AsyncClient)


@pytest.mark.asyncio
async def test_request_raises_not_found_if_stars_recipient_not_found(
    fragment_client_mock: MagicMock,
) -> None:
    fragment_client_mock.return_value = {"error": "No Telegram users found."}

    with pytest.raises(FragmentUsersNotFound):
        await fragment_rest.request(
            method="searchStarsRecipient", data={"query": "anything", "quantity": "50"}
        )


def test_session_is_none_by_default():
    assert fragment_rest._session is None

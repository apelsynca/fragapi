from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from src.fragment_rest.exceptions import FragmentUserNotFound
from src.fragment_rest.main import FragmentRest


@pytest.fixture(autouse=True)
def fragment_client_mock(mocker: MockerFixture) -> MagicMock:
    mocker.patch("src.fragment_rest.fragment_rest.load_session", return_value=None)
    return mocker.patch("src.fragment_rest.fragment_rest.client", spec=AsyncClient)


@pytest.mark.asyncio
async def test_request_raises_not_found_if_stars_recipient_not_found(
    fragment_rest: FragmentRest,
    fragment_client_mock: MagicMock,
) -> None:
    fragment_client_mock.return_value = {"error": "No Telegram users found."}

    with pytest.raises(FragmentUserNotFound):
        await fragment_rest.request(
            method="searchStarsRecipient", data={"query": "anything", "quantity": "50"}
        )

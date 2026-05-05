from time import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.fragment_rest.models import FragmentSession
from src.fragment_rest.rest import FragmentRest
from tests.fixtures.random_objects import lstr, rstr


@pytest.fixture
def fragment_rest(ton_connect, fragment_session: FragmentSession) -> FragmentRest:
    fragment_rest = FragmentRest(ton_connect)

    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._auth = MagicMock(sepc=FragmentRestAuth)
    fragment_rest._last_session_check = time() + fragment_rest.SESSION_LT + 9999

    fragment_rest._session = fragment_session

    return fragment_rest


@pytest.fixture
def fragment_rest_request(fragment_rest: FragmentRest, mocker: MockerFixture) -> None:
    return mocker.patch.object(fragment_rest, "_request", AsyncMock())


@pytest.mark.asyncio
async def test_search_stars_recipient(
    fragment_rest: FragmentRest, fragment_rest_request
) -> None:
    fragment_rest_request.return_value = {
        "ok": True,
        "found": {
            "myself": False,
            "recipient": lstr("somerecipienthash"),
            "photo": "<img src='blablabla' />",
            "name": "Some Name",
        },
        "someotherbs": rstr("randshit"),
    }

    recipient_data = await fragment_rest.search_stars_recipient(
        query="apelsin", quantity=50
    )

    fragment_rest_request.assert_called_once_with(
        method="searchStarsRecipient", data={"query": "apelsin", "quantity": 50}
    )

    assert recipient_data.ok is True
    assert recipient_data.found.myself is False
    assert recipient_data.found.recipient is not None


@pytest.mark.asyncio
async def test_search_stars_recipient_validation_error(
    fragment_rest: FragmentRest, fragment_rest_request
) -> None:
    fragment_rest_request.return_value = {}

    with pytest.raises(ValidationError):
        await fragment_rest.search_stars_recipient(query="apelsin")

    fragment_rest_request.assert_called_once_with(
        method="searchStarsRecipient", data={"query": "apelsin", "quantity": ""}
    )

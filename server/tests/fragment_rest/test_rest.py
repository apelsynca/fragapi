from time import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.fragment_rest.exceptions import FragmentAPIPageError
from src.fragment_rest.models import FragmentSession, MainPageTokens
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
    fragment_rest: FragmentRest, fragment_rest_request: MagicMock
) -> None:
    fragment_rest_request.return_value = {}

    with pytest.raises(ValidationError):
        await fragment_rest.search_stars_recipient(query="apelsin")

    fragment_rest_request.assert_called_once_with(
        method="searchStarsRecipient", data={"query": "apelsin", "quantity": ""}
    )


@pytest.mark.asyncio
async def test_gets_cached_ton_rate_if_no_time(fragment_rest: FragmentRest) -> None:
    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._ton_rate_ut = time() + 1
    fragment_rest._cached_ton_rate = 1.05

    ton_rate = await fragment_rest.get_ton_rate()
    assert ton_rate == 1.05

    fragment_rest._api.get_main_page_tokens.assert_not_called()


@pytest.mark.asyncio
async def test_gets_fresh_ton_rate_if_expired(fragment_rest: FragmentRest) -> None:
    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._ton_rate_ut = 0
    fragment_rest._cached_ton_rate = 1.62

    fragment_rest._api.get_main_page_tokens.return_value = MainPageTokens(
        hash="canbeany", ton_proof_payload="canbeany", ton_rate=2.192
    )

    ton_rate = await fragment_rest.get_ton_rate()
    assert ton_rate == 2.192

    fragment_rest._api.get_main_page_tokens.assert_called_once_with()


@pytest.mark.asyncio
async def test_returns_cached_if_main_page_tokens_fails(
    fragment_rest: FragmentRest,
) -> None:
    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._ton_rate_ut = 0
    fragment_rest._cached_ton_rate = 1.85

    fragment_rest._api.get_main_page_tokens.side_effect = FragmentAPIPageError()

    ton_rate = await fragment_rest.get_ton_rate()
    assert ton_rate == 1.85

    fragment_rest._api.get_main_page_tokens.assert_called_once_with()


@pytest.mark.asyncio
async def test_raises_if_cached_none_and_main_page_fails(
    fragment_rest: FragmentRest,
) -> None:
    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._ton_rate_ut = 0
    fragment_rest._cached_ton_rate = None

    fragment_rest._api.get_main_page_tokens.side_effect = FragmentAPIPageError()

    with pytest.raises(FragmentAPIPageError):
        await fragment_rest.get_ton_rate()

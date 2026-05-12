from time import time

import pytest
from pytest_mock import MockerFixture

from src.fragment.main import Fragment
from src.fragment.models import MainPageTokens
from src.fragment.rest_client import FragmentRestClient
from src.fragment.types import FoundRecipientData, RecipientData
from tests.fixtures.random_objects import rstr


@pytest.fixture
def fragment(rest_client: FragmentRestClient) -> Fragment:
    return Fragment(clients=[rest_client])


@pytest.mark.asyncio
async def test_search_stars_recipient(
    fragment: Fragment, rest_client: FragmentRestClient, mocker: MockerFixture
) -> None:
    api_request_mock = mocker.patch.object(
        rest_client,
        "api_request",
        return_value={
            "ok": True,
            "found": {
                "myself": False,
                "recipient": "somerecipientstring",
                "photo": "somephoto",
                "name": "somename",
            },
        },
    )

    data = await fragment.search_stars_recipient(query="someusername", quantity=52)

    api_request_mock.assert_called_once_with(
        method="searchStarsRecipient", data={"query": "someusername", "quantity": "52"}
    )

    assert data == RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=False,
            recipient="somerecipientstring",
            photo="somephoto",
            name="somename",
        ),
    )


@pytest.mark.asyncio
async def test_get_ton_usd_rate_if_cache_expired(
    fragment: Fragment, rest_client: FragmentRestClient, mocker: MockerFixture
) -> None:
    fragment._last_cache_ut = 0
    fragment._cached_ton_rate = 3.22

    main_page_tokens = MainPageTokens(
        hash=rstr("hash"), ton_proof_payload=rstr("payload"), ton_rate=2.11
    )
    get_mp_tokens_mock = mocker.patch.object(
        rest_client,
        "get_main_page_tokens",
        return_value=main_page_tokens,
    )

    ton_rate = await fragment.get_ton_usd_rate()

    get_mp_tokens_mock.assert_called_once()
    assert ton_rate == 2.11


@pytest.mark.asyncio
async def test_get_ton_rate_from_cache_if_not_expired(
    fragment: Fragment, rest_client: FragmentRestClient, mocker: MockerFixture
) -> None:
    fragment._last_cache_ut = time() + 999
    fragment._cached_ton_rate = 3.22

    get_mp_tokens_mock = mocker.patch.object(
        rest_client,
        "get_main_page_tokens",
    )

    ton_rate = await fragment.get_ton_usd_rate()
    assert ton_rate == 3.22

    get_mp_tokens_mock.assert_not_called()


@pytest.mark.asyncio
async def test_get_ton_rate_not_from_cache_if_cached_ton_rate_is_none(
    fragment: Fragment, rest_client: FragmentRestClient, mocker: MockerFixture
) -> None:
    fragment._last_cache_ut = time() + 999
    fragment._cached_ton_rate = None

    main_page_tokens = MainPageTokens(
        hash=rstr("hash"), ton_proof_payload=rstr("payload"), ton_rate=1.882
    )
    get_mp_tokens_mock = mocker.patch.object(
        rest_client,
        "get_main_page_tokens",
        return_value=main_page_tokens,
    )

    ton_rate = await fragment.get_ton_usd_rate()
    assert ton_rate == 1.882

    get_mp_tokens_mock.assert_called_once()


# TODO: Test gets random client

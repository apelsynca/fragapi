from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient, Cookies, Response

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.exceptions import (
    FragmentAPIAccessDenied,
    FragmentAPIBadRequest,
    FragmentAPIPageError,
    FragmentAPIUsersNotFound,
)
from src.fragment_rest.models import MainPageTokens
from tests.fixtures.random_objects import rstr
from tests.fragment_rest.test_auth import generate_fake_main_page_text


@pytest.fixture
def fragment_api_client() -> FragmentAPIClient:
    frag_client = FragmentAPIClient()
    frag_client._client = MagicMock(spec=AsyncClient)
    frag_client._client.post.return_value = Response(status_code=404)

    return frag_client


@pytest.mark.asyncio
async def test_request_raises_if_not_found(
    fragment_api_client: FragmentAPIClient,
) -> None:
    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.post.return_value = Response(
        status_code=200, json={"error": "No Telegram users found."}
    )

    with pytest.raises(FragmentAPIUsersNotFound):
        await fragment_api_client.request(
            hash="somehash", method=rstr("method"), data={"somedata": "yes"}
        )


@pytest.mark.asyncio
async def test_request_raises_if_access_denied(
    fragment_api_client: FragmentAPIClient,
) -> None:
    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.post.return_value = Response(
        status_code=200, json={"error": "Access denied"}
    )

    with pytest.raises(FragmentAPIAccessDenied):
        await fragment_api_client.request(
            hash="otherhash", method=rstr("method"), data={"somedata": rstr("yeah")}
        )


@pytest.mark.asyncio
async def test_request_unknown_error_raises(
    fragment_api_client: FragmentAPIClient,
) -> None:
    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.post.return_value = Response(
        status_code=200, json={"error": "Some unknown to anyone error"}
    )

    with pytest.raises(FragmentAPIBadRequest):
        await fragment_api_client.request(
            hash=rstr("hashik"), method="getStarsRecipient", data={}
        )


@pytest.mark.asyncio
async def test_request_returns_response_json_on_200(
    fragment_api_client: FragmentAPIClient,
) -> None:
    mock_data = {"real": "mock", "someOther": "mock"}

    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.post.return_value = Response(
        status_code=200, json=mock_data
    )

    json = await fragment_api_client.request(
        hash=rstr("hashik"), method="someMethodName", data={}
    )

    assert json == mock_data


@pytest.mark.asyncio
async def test_ignores_irrelevant_cookies(
    fragment_api_client: FragmentAPIClient,
) -> None:
    random_abc = rstr("session")
    all_cookies = {
        "abrikos": "somethng",
        "other": None,
        "value": "smth",
        "stel_dt": "-360",
        "stel_ssid": random_abc,
        "stel_ton_token": None,
    }

    fragment_api_client._client.cookies = Cookies(all_cookies)

    relevant_cookies = fragment_api_client.get_client_relevant_cookies()

    assert "abrikos" not in relevant_cookies
    assert "other" not in relevant_cookies

    assert relevant_cookies["stel_dt"] == "-360"
    assert relevant_cookies["stel_ssid"] == random_abc
    assert relevant_cookies["stel_ton_token"] is None


@pytest.mark.asyncio
async def test_get_main_page_return_right_tokens(
    fragment_api_client: FragmentAPIClient,
) -> None:
    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.get.return_value = Response(
        status_code=200,
        text=generate_fake_main_page_text(
            hash="somehashik", ton_proof="sometonproofik", ton_rate=15.5254
        ),
    )

    tokens = await fragment_api_client.get_main_page_tokens()

    assert tokens == MainPageTokens(
        hash="somehashik", ton_proof_payload="sometonproofik", ton_rate=15.5254
    )


@pytest.mark.asyncio
async def test_get_main_page_tokens_raises(
    fragment_api_client: FragmentAPIClient,
) -> None:
    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.get.return_value = Response(status_code=404)

    with pytest.raises(FragmentAPIPageError):
        await fragment_api_client.get_main_page_tokens()

    fragment_api_client._client.get.assert_called_once()

from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient, Response
from tonutils.contracts import WalletV5R1

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.exceptions import (
    FragmentAPIBadRequest,
    FragmentAPIError,
    FragmentAPINotAuthorized,
    FragmentAPIUsersNotFound,
)
from src.fragment_rest.models import FragmentSession
from src.kit.ton_connect import TonConnect


@pytest.fixture
def fragment_api_client(ton_connect: TonConnect) -> FragmentAPIClient:
    frag_client = FragmentAPIClient(ton_connect=ton_connect)
    frag_client._client = MagicMock(spec=AsyncClient)

    return frag_client


def test_raises_runtime_if_bad_ton_connect_domain():
    with pytest.raises(RuntimeError):
        FragmentAPIClient(
            ton_connect=TonConnect(
                wallet=MagicMock(spec=WalletV5R1), tc_domain="wrongdomain.com"
            )
        )


@pytest.mark.asyncio
async def test_get_main_page_raises(fragment_api_client: FragmentAPIClient) -> None:
    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.get.return_value = Response(status_code=404)

    with pytest.raises(FragmentAPIError):
        await fragment_api_client.get_main_page()

    fragment_api_client._client.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_main_returns_text(fragment_api_client: FragmentAPIClient) -> None:
    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.get.return_value = Response(
        status_code=200, text="AbracadaBRa page"
    )

    text = await fragment_api_client.get_main_page()
    assert text == "AbracadaBRa page"

    fragment_api_client._client.get.assert_called_once()


@pytest.mark.asyncio
async def test_request_raises_if_not_authorized(
    fragment_api_client: FragmentAPIClient,
) -> None:
    assert fragment_api_client._session is None

    with pytest.raises(FragmentAPINotAuthorized):
        await fragment_api_client.request(method="getStarsRecipient", data={})


@pytest.mark.asyncio
async def test_request_raises_if_not_found(
    fragment_api_client: FragmentAPIClient,
) -> None:
    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.post.return_value = Response(
        status_code=200, json={"error": "No Telegram users found."}
    )
    fragment_api_client._session = FragmentSession(
        hash="somehash", ton_proof="some ton_proof", cookies={}
    )

    with pytest.raises(FragmentAPIUsersNotFound):
        await fragment_api_client.request(
            method="getStarsRecipient", data={"somedata": "yes"}
        )


@pytest.mark.asyncio
async def test_request_unknown_error_raises(
    fragment_api_client: FragmentAPIClient,
) -> None:
    fragment_api_client._client = MagicMock(spec=AsyncClient)
    fragment_api_client._client.post.return_value = Response(
        status_code=200, json={"error": "Some unknown to anyone error"}
    )
    fragment_api_client._session = FragmentSession(
        hash="somehash", ton_proof="some ton_proof", cookies={}
    )

    with pytest.raises(FragmentAPIBadRequest):
        await fragment_api_client.request(method="getStarsRecipient", data={})

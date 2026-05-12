from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from src.fragment.main import Fragment
from src.fragment.rest_client import FragmentRestClient
from src.fragment.rest_request import BaseClient
from src.fragment.session_storage import FragmentSession
from src.fragment.types import FoundRecipientData, RecipientData
from src.kit.ton_connect import TonConnect


@pytest.fixture
def fragment_rest_client(
    ton_connect: TonConnect, mocker: MockerFixture
) -> FragmentRestClient:
    client = FragmentRestClient(ton_connect=ton_connect, session_key="thesession")
    client.session_storage.session = FragmentSession(
        hash="SessionHash", ton_proof_payload="SessionPayload", cookies={}
    )
    client._client = AsyncMock(spec=BaseClient)

    return client


@pytest.mark.asyncio
async def test_search_stars_recipient(
    fragment_rest_client: FragmentRestClient, mocker: MockerFixture
) -> None:
    fragment = Fragment(clients=[fragment_rest_client])

    api_request_mock = mocker.patch.object(
        fragment_rest_client,
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


# Test gets random client

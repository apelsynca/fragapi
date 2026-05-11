from time import time
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.fragment.exceptions import (
    FragmentAPIError,
    FragmentAPIUsersNotFound,
    FragmentError,
)
from src.fragment.rest_client import FragmentRestClient
from src.fragment.rest_request import BaseRequest
from src.fragment.session_storage import FragmentSession
from tests.fragment.helpers import MockRequest


@pytest.fixture
def valid_frag_session() -> FragmentSession:
    return FragmentSession(hash="eecc", ton_proof_payload="bbdd", cookies={})


@pytest.fixture
def rest_client(mocker: MockerFixture, ton_connect: MagicMock) -> FragmentRestClient:
    mocker.patch(
        "src.fragment.rest_client.SessionStorage.load_session", return_value=None
    )
    client = FragmentRestClient(ton_connect=ton_connect, session_key="phd")
    client._request = MagicMock(spec=BaseRequest)
    client._request.do_request.return_value = (200, b"{}", {})
    client.last_session_check = time()
    return client


@pytest.mark.asyncio
async def test_request_calls_reauth_if_cache_time_stale(
    rest_client: FragmentRestClient, mocker: MockerFixture
) -> None:
    rest_client.last_session_check = 0
    rest_client.session_storage.session = FragmentSession(
        hash="hash", ton_proof_payload="tonproof", cookies={}
    )
    spy = mocker.spy(rest_client, "ensure_session_correct_tokens")

    await rest_client.api_request(method="someCoolMethod", data={"abc": "def"})

    spy.assert_called_once()


@pytest.mark.asyncio
async def test_request_does_not_call_reauth_if_cache_time_stale(
    rest_client: FragmentRestClient, mocker: MockerFixture
) -> None:
    rest_client.last_session_check = time() + 9999
    rest_client.session_storage.session = FragmentSession(
        hash="hash", ton_proof_payload="tonproof", cookies={}
    )
    ensure_session_spy = mocker.spy(rest_client, "ensure_session_correct_tokens")

    await rest_client.api_request(method="someCoolMethod", data={"abc": "def"})

    ensure_session_spy.assert_not_called()


@pytest.mark.asyncio
async def test_raises_if_api_request_without_session(
    rest_client: FragmentRestClient, mocker: MockerFixture
) -> None:
    rest_client.last_session_check = time() + 9999
    rest_client.session_storage.session = None
    ensure_session_spy = mocker.spy(rest_client, "ensure_session_correct_tokens")

    with pytest.raises(FragmentError):
        await rest_client.api_request(method="someCoolMethod", data={"data": "def"})

    ensure_session_spy.assert_not_called()


@pytest.mark.asyncio
async def test_request_right_call_data(
    rest_client: FragmentRestClient,
    mocker: MockerFixture,
    valid_frag_session: FragmentSession,
) -> None:
    rest_client.session_storage.session = valid_frag_session

    spy = mocker.spy(rest_client._request, "do_request")

    await rest_client.api_request(method="doSomeThinkOnFrag", data={"abc": "cde"})

    data = {"method": "doSomeThinkOnFrag", "abc": "cde"}

    hash = rest_client.session_storage.session.hash
    spy.assert_called_once_with(
        url=f"https://fragment.com/api?hash={hash}", method="POST", json_data=data
    )


@pytest.mark.asyncio
async def test_api_request_raises_if_resp_non_200(
    rest_client: FragmentRestClient,
    valid_frag_session: FragmentSession,
) -> None:
    mock_request = MockRequest()
    mock_request.return_status_code = 404

    rest_client._request = mock_request
    rest_client.session_storage.session = valid_frag_session

    with pytest.raises(FragmentError):
        await rest_client.api_request(method="someMethod", data={"any": "data"})


@pytest.mark.asyncio
async def test_raises_if_method_in_data(
    rest_client: FragmentRestClient,
    valid_frag_session: FragmentSession,
) -> None:
    rest_client.session_storage.session = valid_frag_session

    with pytest.raises(
        ValueError, match="Cannot include key method in api_request.data"
    ):
        await rest_client.api_request(
            method="someMethod", data={"method": "differentMethod"}
        )


@pytest.mark.asyncio
async def test_api_request_parses_errors(
    rest_client: FragmentRestClient,
    valid_frag_session: FragmentSession,
) -> None:
    rest_client.session_storage.session = valid_frag_session


@pytest.mark.asyncio
async def test_return_right_json_data(
    rest_client: FragmentRestClient,
    valid_frag_session: FragmentSession,
) -> None:
    rest_client.session_storage.session = valid_frag_session
    rest_client._request = MockRequest(
        return_status_code=200, return_json={"some": "data", "withExternal": "values"}
    )

    data = await rest_client.api_request(
        method="doSomeThinkOnFrag", data={"abc": "cde"}
    )

    assert data == {"some": "data", "withExternal": "values"}


@pytest.mark.asyncio
async def test_if_error_just_raises_it(
    rest_client: FragmentRestClient,
    valid_frag_session: FragmentSession,
) -> None:
    error_text = "Some kind of bad error"

    rest_client.session_storage.session = valid_frag_session
    rest_client._request = MockRequest(
        return_status_code=200,
        return_json={"some": "data", "withExternal": "values", "error": error_text},
    )

    with pytest.raises(FragmentAPIError, match=error_text):
        await rest_client.api_request(method="doSomeThinkOnFrag", data={"abc": "cde"})


@pytest.mark.asyncio
async def test_detect_users_not_found_error(
    rest_client: FragmentRestClient,
    valid_frag_session: FragmentSession,
) -> None:
    rest_client.session_storage.session = valid_frag_session
    rest_client._request = MockRequest(
        return_status_code=200,
        return_json={
            "some": "data",
            "withExternal": "values",
            "error": "No Telegram users found.",
        },
    )

    with pytest.raises(FragmentAPIUsersNotFound):
        await rest_client.api_request(method="doSomeThinkOnFrag", data={"abc": "cde"})

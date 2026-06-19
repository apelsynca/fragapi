from time import time

import pytest
from pytest_mock import MockerFixture

from src.integrations.fragment.exceptions import (
    FragmentAPIError,
    FragmentAPIUsersNotFound,
    FragmentError,
)
from src.integrations.fragment.rest_client import FragmentRestClient
from src.integrations.fragment.session_storage import FragmentSession
from tests.integrations.fragment.helpers import MockClient


@pytest.mark.asyncio
async def test_raises_if_api_request_without_session(
    rest_client: FragmentRestClient, mocker: MockerFixture
) -> None:
    rest_client.last_session_check = time() + 9999  # no matter
    rest_client.session_storage.session = None
    ensure_session_spy = mocker.spy(rest_client, "_is_correct_session_tokens")

    with pytest.raises(FragmentError):
        await rest_client.api_request(method="someCoolMethod", data={"data": "def"})

    ensure_session_spy.assert_not_called()


@pytest.mark.asyncio
async def test_does_request_with_right_data(
    rest_client: FragmentRestClient,
    mocker: MockerFixture,
    valid_frag_session: FragmentSession,
) -> None:
    rest_client.session_storage.session = valid_frag_session

    spy = mocker.spy(rest_client._client, "do_request")

    await rest_client.api_request(method="doSomeThinkOnFrag", data={"abc": "cde"})

    data = {"method": "doSomeThinkOnFrag", "abc": "cde"}

    hash = rest_client.session_storage.session.hash
    spy.assert_called_once_with(
        url=f"https://fragment.com/api?hash={hash}",
        method="POST",
        form_data=data,
        headers={"X-Requested-With": "XMLHttpRequest"},
    )


@pytest.mark.asyncio
async def test_raises_if_method_in_data(
    rest_client: FragmentRestClient,
) -> None:
    with pytest.raises(
        ValueError, match="Cannot include key method in api_request.data"
    ):
        await rest_client.api_request(
            method="someMethod", data={"method": "differentMethod"}
        )


@pytest.mark.asyncio
async def test_if_error_just_raises_it(
    rest_client: FragmentRestClient,
    valid_frag_session: FragmentSession,
) -> None:
    error_text = "Some kind of bad error"

    rest_client.session_storage.session = valid_frag_session
    rest_client._client = MockClient(
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
    rest_client._client = MockClient(
        return_status_code=200,
        return_json={
            "some": "data",
            "withExternal": "values",
            "error": "No Telegram users found.",
        },
    )

    with pytest.raises(FragmentAPIUsersNotFound):
        await rest_client.api_request(method="doSomeThinkOnFrag", data={"abc": "cde"})


@pytest.mark.asyncio
async def test_return_right_json_data(
    rest_client: FragmentRestClient,
    valid_frag_session: FragmentSession,
) -> None:
    rest_client.session_storage.session = valid_frag_session
    rest_client._client = MockClient(
        return_status_code=200, return_json={"some": "data", "withExternal": "values"}
    )

    data = await rest_client.api_request(
        method="doSomeThinkOnFrag", data={"abc": "cde"}
    )

    assert data == {"some": "data", "withExternal": "values"}


# PERF: There is a lot to test, especcialy in terms of the auth, but i'm concerned with different stuff

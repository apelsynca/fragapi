import json
from time import time
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.fragment.exceptions import FragmentError
from src.fragment.rest_client import FragmentRestClient
from src.fragment.rest_request import BaseRequest
from src.fragment.session_storage import FragmentSession


class MockRequest(BaseRequest):
    def __init__(self) -> None:
        self.return_status_code = 404
        self.return_json = None
        self.return_text = None
        self.return_cookies = {}

    async def do_request(
        self, url: str, method: str, json_data: dict | None = None
    ) -> tuple[int, bytes, dict[str, str]]:
        if self.return_json and self.return_text:
            raise RuntimeError("Cannot do both self.return_json and self.return_text")

        content = b""
        if self.return_json:
            content = json.dumps(self.return_json).encode("utf-8")
        if self.return_text:
            content = self.return_text.encode("utf-8")

        return (
            self.return_status_code,
            content,
            self.return_cookies,
        )


@pytest.fixture
def valid_frag_session() -> FragmentSession:
    return FragmentSession(hash="", ton_proof_payload="", cookies={})


@pytest.fixture
def rest_client(mocker: MockerFixture, ton_connect: MagicMock) -> FragmentRestClient:
    mocker.patch(
        "src.fragment.rest_client.SessionStorage.load_session", return_value=None
    )
    client = FragmentRestClient(ton_connect=ton_connect, session_key="phd")
    client._request = MagicMock(spec=MockRequest)
    client._request.do_request.return_value = (404, b"", {})
    return client


@pytest.mark.asyncio
async def test_request_right_call_data(
    rest_client: FragmentRestClient,
    mocker: MockerFixture,
    valid_frag_session: FragmentSession,
) -> None:
    rest_client._request = MockRequest()
    rest_client.session_storage.session = valid_frag_session

    spy = mocker.spy(rest_client._request, "do_request")

    await rest_client.api_request(method="doSomeThinkOnFrag", data={"abc": "cde"})

    data = {}

    hash = rest_client.session_storage.session.hash
    spy.assert_called_once_with(
        url=f"https://fragment.com/api?hash={hash}", method="POST", json_data=data
    )


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
):
    rest_client.last_session_check = time() + 9999
    rest_client.session_storage.session = None
    ensure_session_spy = mocker.spy(rest_client, "ensure_session_correct_tokens")

    with pytest.raises(FragmentError):
        await rest_client.api_request(method="someCoolMethod", data={"data": "def"})

    ensure_session_spy.assert_not_called()

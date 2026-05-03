from unittest.mock import ANY, AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.fragment_rest.models import FragmentSession
from src.kit.ton_connect import TonConnectRequestData


@pytest.fixture
def fragment_session() -> FragmentSession:
    return FragmentSession(
        hash="thesupersessionhash",
        ton_proof_payload="thedatafortonconnect",
        cookies={},
    )


@pytest.fixture
def fragment_api_client() -> AsyncMock:
    mock = AsyncMock(spec=FragmentAPIClient)

    mock.base_url = "httsp://database.com"

    return mock


@pytest.fixture
def fragment_rest_auth(
    mocker: MockerFixture,
    ton_connect,
) -> FragmentRestAuth:
    mocker.patch.object(FragmentRestAuth, "load_session", return_value=None)

    fragment_rest_auth = FragmentRestAuth(ton_connect=ton_connect)
    fragment_rest_auth.has_authorized = True

    return fragment_rest_auth


@pytest.mark.asyncio
async def test_gets_right_session_tokens(
    fragment_rest_auth: FragmentRestAuth, fragment_api_client: AsyncMock
) -> None:
    fragment_api_client.get_main_page.return_value = (
        "<html>...somethign<div></div><script>\n"
        'ajInit({"version":589,"apiUrl":"\\/api?hash=a883d11d2fc9somehash","state":{"quickSearch":false,"tonRate":1.33501149}});\n'
        "</script>\n"
        "<script>\n"
        "Aj._useScrollHack=true;\n"
        "Main.init();\n"
        'Wallet.init({"address":"0:25203b4f773a967f6c6310b9aa555acdaa81a87dfa0a386a9de2db6a8f3c8f19","ton_proof":"5550ffd0ff31a55ca4","logged_in":true,"version":2});\n'
        "</script>"
    )

    fragment_session = await fragment_rest_auth.get_online_session(fragment_api_client)

    assert fragment_session == FragmentSession(
        hash="a883d11d2fc9somehash",
        ton_proof_payload="5550ffd0ff31a55ca4",
        cookies=fragment_session.cookies,
    )


@pytest.mark.asyncio
async def test_authorize_does_not_authorize_if_already_authorized() -> None:
    pass


@pytest.mark.asyncio
async def test_authorize_dont_authorize_if_check_auth_and_session() -> None:
    pass


@pytest.mark.asyncio
async def test_authorize_dont_if_authorized_and_last_auth_fresh() -> None:
    pass


@pytest.mark.asyncio
async def test_authorize_does_if_authorized_and_last_auth_old() -> None:
    pass


@pytest.mark.asyncio
async def test_authorize_tries_to_load_session(
    mocker: MockerFixture,
    fragment_rest_auth: FragmentRestAuth,
) -> None:
    load_session_mock = mocker.patch.object(fragment_rest_auth, "load_session")
    await fragment_rest_auth.authorize()
    load_session_mock.assert_called_once()


@pytest.mark.asyncio
async def test_check_auth_does_not_request_if_not_authorized(
    fragment_rest_auth: FragmentRestAuth, fragment_api_client: AsyncMock
) -> None:
    fragment_rest_auth.has_authorized = False

    authed = await fragment_rest_auth.check_session(
        api_client=fragment_api_client,
        session=FragmentSession(hash="hash", ton_proof_payload="someProof", cookies={}),
    )
    assert authed is False

    fragment_api_client.request.assert_not_called()


@pytest.mark.asyncio
async def test_check_auth_calls_api_if_was_authorized(
    fragment_rest_auth: FragmentRestAuth,
    fragment_api_client: AsyncMock,
    ton_connect: MagicMock,
    fragment_session: FragmentSession,
) -> None:
    assert fragment_rest_auth.has_authorized is True

    # ton connect returns
    ton_connect.get_connect_request_data.return_value = TonConnectRequestData(
        account={}, proof={}, device={}
    )
    fragment_api_client.request.return_value = {"verified": True}

    await fragment_rest_auth.check_session(
        api_client=fragment_api_client,
        session=fragment_session,
    )

    fragment_api_client.request.assert_called_once_with(
        method="checkTonProofAuth",
        data=ANY,
        headers={"X-Requested-With": "XMLHttpRequest"},
        check_authorized=False,
    )


@pytest.mark.asyncio
async def test_check_calls_ton_connect_request_data(
    fragment_rest_auth: FragmentRestAuth,
    fragment_api_client: AsyncMock,
    ton_connect,
    fragment_session: FragmentSession,
) -> None:
    assert fragment_rest_auth.has_authorized is True

    request_data_model = TonConnectRequestData(
        proof={"hello": "world"},
        account={"accountInfo": "someinfo"},
        device={"hash_type": "321231"},
    )
    ton_connect.get_connect_request_data.return_value = request_data_model
    fragment_api_client.request.return_value = {}

    await fragment_rest_auth.check_session(
        api_client=fragment_api_client, session=fragment_session
    )

    ton_connect.get_connect_request_data.assert_called_once_with(
        ton_proof_payload=fragment_session.ton_proof_payload
    )
    fragment_api_client.request.assert_called_once_with(
        method="checkTonProofAuth",
        data=request_data_model.model_dump(),
        headers=ANY,
        check_authorized=False,
    )

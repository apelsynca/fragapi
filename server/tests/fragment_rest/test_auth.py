from unittest.mock import ANY, AsyncMock, MagicMock

import pytest
from tonutils.contracts import WalletV5R1

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.fragment_rest.models import FragmentSession
from src.kit.ton_connect import TonConnect, TonConnectRequestData


@pytest.fixture
def fragment_api_client() -> AsyncMock:
    mock = AsyncMock(spec=FragmentAPIClient)

    mock.base_url = "httsp://database.com"

    return mock


@pytest.fixture
def fragment_rest_auth(ton_connect) -> FragmentRestAuth:
    return FragmentRestAuth(ton_connect=ton_connect)


def generate_fake_main_page_text(hash: str, ton_proof: str) -> str:
    return (
        "<html>...somethign<div></div><script>\n"
        f'ajInit({{"version":589,"apiUrl":"\\/api?hash={hash}","state":{{"quickSearch":false,"tonRate":1.33501149}}}});\n'
        "</script>\n"
        "<script>\n"
        "Aj._useScrollHack=true;\n"
        "Main.init();\n"
        f'Wallet.init({{"address":"0:25203b4f773a967f6c6310b9aa555acdaa81a87dfa0a386a9de2db6a8f3c8f19","ton_proof":"{ton_proof}","logged_in":true,"version":2}});\n'
        "</script>"
    )


def test_raises_runtime_if_bad_ton_connect_domain():
    with pytest.raises(RuntimeError):
        FragmentRestAuth(
            ton_connect=TonConnect(
                wallet=MagicMock(spec=WalletV5R1), tc_domain="wrongdomain.com"
            )
        )


@pytest.mark.asyncio
async def test_gets_right_session_tokens(
    fragment_rest_auth: FragmentRestAuth, fragment_api_client: AsyncMock
) -> None:
    fragment_api_client.get_main_page.return_value = generate_fake_main_page_text(
        hash="a883d11d2fc9somehash", ton_proof="5550ffd0ff31a55ca4"
    )

    fragment_session = await fragment_rest_auth.get_online_session(fragment_api_client)

    assert fragment_session == FragmentSession(
        hash="a883d11d2fc9somehash",
        ton_proof_payload="5550ffd0ff31a55ca4",
        cookies=fragment_session.cookies,
    )


@pytest.mark.asyncio
async def test_check_auth_calls_api_if_was_authorized(
    fragment_rest_auth: FragmentRestAuth,
    fragment_api_client: AsyncMock,
    ton_connect: MagicMock,
    fragment_session: FragmentSession,
) -> None:
    # ton connect returns
    ton_connect.get_connect_request_data.return_value = TonConnectRequestData(
        account={}, proof={}, device={}
    )
    fragment_api_client.request.return_value = {"verified": True}

    verified = await fragment_rest_auth.check_session(
        api_client=fragment_api_client,
        session=fragment_session,
    )

    fragment_api_client.request.assert_called_once_with(
        hash=fragment_session.hash,
        method="checkTonProofAuth",
        data=ANY,
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    assert verified is True


@pytest.mark.asyncio
async def test_check_calls_ton_connect_request_data(
    fragment_rest_auth: FragmentRestAuth,
    fragment_api_client: AsyncMock,
    ton_connect,
    fragment_session: FragmentSession,
) -> None:
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


@pytest.mark.asyncio
async def test_get_online_session_saves_cookies(
    fragment_rest_auth: FragmentRestAuth, fragment_api_client: AsyncMock
) -> None:
    target_cookies = {"some-cookie": "some-value", "other": "other-value"}
    fragment_api_client.get_client_relevant_cookies.return_value = target_cookies
    fragment_api_client.get_main_page.return_value = generate_fake_main_page_text(
        hash="any", ton_proof="any"
    )

    fragment_session = await fragment_rest_auth.get_online_session(fragment_api_client)

    assert fragment_session.cookies == target_cookies

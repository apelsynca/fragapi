import random
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.integrations.fragment.models import MainPageTokens
from src.integrations.fragment.rest_client import FragmentRestClient
from src.integrations.fragment.rest_request import BaseClient
from src.integrations.fragment.session_storage import FragmentSession
from src.kit.ton_connect import TonConnect


@pytest.fixture
def ton_connect() -> MagicMock:
    ton_connect = MagicMock(spec=TonConnect)

    ton_connect.tc_domain = "fragment.com"

    return ton_connect


@pytest.fixture(autouse=True)
def session_storage_load_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.integrations.fragment.rest_client.SessionStorage.load", return_value=None
    )


@pytest.fixture
def valid_frag_session() -> FragmentSession:
    return FragmentSession(hash="eecc", ton_proof_payload="bbdd", cookies={})


@pytest.fixture
def rest_client(
    ton_connect: MagicMock, mocker: MockerFixture, valid_frag_session: FragmentSession
) -> FragmentRestClient:
    client = FragmentRestClient(ton_connect=ton_connect, session_key="any")

    client._client = MagicMock(spec=BaseClient)
    client._client.do_request.return_value = (200, b"{}")
    client.last_session_check = 0

    client.session_storage.session = valid_frag_session
    mocker.patch.object(
        client,
        "get_main_page_tokens",
        return_value=MainPageTokens(
            hash=valid_frag_session.hash,
            ton_proof_payload=valid_frag_session.ton_proof_payload,
            ton_rate=random.randint(1, 500) / 100,
        ),
    )

    return client


def generate_fake_main_page_text(hash: str, ton_proof: str, ton_rate: float) -> str:
    return (
        "<html>...somethign<div></div><script>\n"
        f'ajInit({{"version":589,"apiUrl":"\\/api?hash={hash}","state":{{"quickSearch":false,"tonRate":{ton_rate:.6f}}}}});\n'
        "</script>\n"
        "<script>\n"
        "Aj._useScrollHack=true;\n"
        "Main.init();\n"
        f'Wallet.init({{"address":"0:25203b4f773a967f6c6310b9aa555acdaa81a87dfa0a386a9de2db6a8f3c8f19","ton_proof":"{ton_proof}","logged_in":true,"version":2}});\n'
        "</script>"
    )

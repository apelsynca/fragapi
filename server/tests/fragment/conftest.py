from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.kit.ton_connect import TonConnect


@pytest.fixture
def ton_connect() -> MagicMock:
    return MagicMock(spec=TonConnect)


@pytest.fixture(autouse=True)
def storage_load_session_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.fragment.rest_client.SessionStorage.load_session", return_value=None
    )


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

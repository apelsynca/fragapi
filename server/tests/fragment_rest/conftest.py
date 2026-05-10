from unittest.mock import MagicMock

import pytest

from src.kit.ton_connect import TonConnect


@pytest.fixture
def ton_connect() -> MagicMock:
    ton_connect_mock = MagicMock(spec=TonConnect)

    ton_connect_mock.tc_domain = "fragment.com"

    return ton_connect_mock


# @pytest.fixture
# def fragment_session() -> FragmentSession:
#     return FragmentSession(
#         hash=lstr("somehash"),
#         ton_proof_payload=rstr("somepayload"),
#         cookies={},
#     )


# @pytest.fixture(autouse=True)
# def load_session_patch(mocker: MockerFixture) -> None:
#     mocker.patch.object(BaseFragmentRest, "_load_session", return_value=None)


# @pytest.fixture(autouse=True)
# def save_session_patch(mocker: MockerFixture):
#     return mocker.patch.object(BaseFragmentRest, "_save_session", return_value=None)


def generate_fake_main_page_text(
    hash: str, ton_proof: str, ton_rate: float = 1.33501149
) -> str:
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

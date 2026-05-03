from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from src.kit.ton_connect import TonConnect, TonConnectRequestData


def test_return_request_data(mocker: MockerFixture):
    ton_connect = TonConnect(wallet=MagicMock(), tc_domain="somedomain.com")

    mocker.patch.object(ton_connect, "get_account", return_value={"accountInfo": "abc"})
    mocker.patch.object(ton_connect, "get_device", return_value={"deviceInfo": "def"})
    mocker.patch.object(ton_connect, "get_proof", return_value={"someproof": "payload"})

    request_data = ton_connect.get_connect_request_data("somepayload")
    assert isinstance(request_data, TonConnectRequestData)

    assert request_data.account == {"accountInfo": "abc"}
    assert request_data.device == {"deviceInfo": "def"}
    assert request_data.proof == {"someproof": "payload"}

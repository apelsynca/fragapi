import json

import pytest
from pytest_mock import MockerFixture

from src.config import settings
from src.fragment_rest.exceptions import FragmentAPIError
from src.fragment_rest.models import FragmentSession, MainPageTokens
from src.fragment_rest.session_manager import FragmentSessionManager
from tests.fixtures.random_objects import rstr


@pytest.fixture
def fragment_session() -> FragmentSession:
    return FragmentSession(
        hash=rstr("hash"),
        ton_proof_payload=rstr("tonproof"),
        cookies={},
        last_session_check=0,
    )


@pytest.fixture
def session_manager(mocker: MockerFixture) -> FragmentSessionManager:
    mocker.patch("builtins.open", mocker.mock_open(read_data="randombs"))

    return FragmentSessionManager()


def test_loads_saved_session(mocker: MockerFixture) -> None:
    ses = FragmentSession(
        hash="some hash",
        ton_proof_payload="some ton proof payload",
        cookies={},
        last_session_check=0,
    )
    data = ses.model_dump()
    mock_open = mocker.patch(
        "builtins.open", mocker.mock_open(read_data=json.dumps(data, indent=2))
    )

    session_manager = FragmentSessionManager()
    assert session_manager._session is None

    session_manager.load_saved()
    mock_open.assert_called_once_with(settings.FRAGMENT_SESSION_PATH)

    assert session_manager._session == ses


def test_if_data_error_raises_runtime(mocker: MockerFixture) -> None:
    mock_open = mocker.patch(
        "builtins.open", mocker.mock_open(read_data="someinvaliddata")
    )

    session_manager = FragmentSessionManager()
    with pytest.raises(RuntimeError):
        session_manager.load_saved()

    mock_open.assert_called_once_with(settings.FRAGMENT_SESSION_PATH)


def test_determines_valid_correctly(session_manager: FragmentSessionManager) -> None:
    session_manager._session = FragmentSession(
        hash="ce7de406bde4540cfc",
        ton_proof_payload="ec4bdf6c8c238f3368",
        cookies={"stel_ssid": "", "stel_token": "", "stel_ton_token": ""},
    )

    is_valid = session_manager.is_valid_session()

    assert is_valid is True


def test_is_valid_session_does_not_modify_session(
    session_manager: FragmentSessionManager,
) -> None:
    session_clone = FragmentSession(
        hash="xxce7de406bde4540cfc",
        ton_proof_payload="ec4bdf6c8c238f3368",
        cookies={"stel_ssid": "abc", "stel_token": "abc", "stel_ton_token": "abc"},
    )
    session_manager._session = session_clone.model_copy()
    is_valid = session_manager.is_valid_session()
    assert is_valid is False

    assert session_manager._session == session_clone


def test_raises_if_no_session_and_check_valid_session(
    session_manager: FragmentSessionManager,
) -> None:
    with pytest.raises(FragmentAPIError):
        session_manager.is_valid_session()


def test_determines_false_if_invalid_hash(
    session_manager: FragmentSessionManager,
) -> None:
    session_manager._session = FragmentSession(
        hash="xxce7de406bde4540cfc",
        ton_proof_payload="ec4bdf6c8c238f3368",
        cookies={"stel_ssid": "abc", "stel_token": "abc", "stel_ton_token": "abc"},
    )
    is_valid = session_manager.is_valid_session()
    assert is_valid is False


def test_determines_false_if_invalid_ton_proof(
    session_manager: FragmentSessionManager,
) -> None:
    session_manager._session = FragmentSession(
        hash="ce7de406bde4540cfc",
        ton_proof_payload="xbad_ec4bdf6c8c238f3368",
        cookies={"stel_ssid": "abc", "stel_token": "abc", "stel_ton_token": "abc"},
    )
    is_valid = session_manager.is_valid_session()
    assert is_valid is False


def test_sets_new_session_and_saves(session_manager: FragmentSessionManager) -> None:
    session = FragmentSession(
        hash="ce7de406bde4540cfc",
        ton_proof_payload="ec4bdf6c8c238f3368",
        cookies={},
        last_session_check=0,
    )

    session_manager.set_session(session)


def test_raises_if_session_to_set_is_invalid(
    session_manager: FragmentSessionManager,
) -> None:
    session = FragmentSession(
        hash="hash", ton_proof_payload="uuuuuuuu", cookies={}, last_session_check=0
    )

    with pytest.raises(FragmentAPIError):
        session_manager.set_session(session)


def test_check_tokens_returns_valid(session_manager: FragmentSessionManager) -> None:
    tokens = MainPageTokens(hash="hash", ton_proof_payload="payload", ton_rate=0)
    session_manager._session = FragmentSession(
        hash="hash", ton_proof_payload="payload", cookies={}, last_session_check=0
    )
    result = session_manager.check_tokens(tokens)

    assert result is True


def test_check_tokens_returns_invalid_if_hash(
    session_manager: FragmentSessionManager,
) -> None:
    tokens = MainPageTokens(hash=rstr("diff"), ton_proof_payload="payload", ton_rate=0)
    session_manager._session = FragmentSession(
        hash="hash", ton_proof_payload="payload", cookies={}, last_session_check=0
    )
    result = session_manager.check_tokens(tokens)

    assert result is False


def test_check_tokens_returns_invalid_if_payload(
    session_manager: FragmentSessionManager,
) -> None:
    tokens = MainPageTokens(hash="hash", ton_proof_payload=rstr("diff"), ton_rate=0)
    session_manager._session = FragmentSession(
        hash="hash", ton_proof_payload="payload", cookies={}, last_session_check=0
    )
    result = session_manager.check_tokens(tokens)

    assert result is False


def test_gets_right_session(session_manager: FragmentSessionManager) -> None:
    assert session_manager._session == session_manager.get_session()

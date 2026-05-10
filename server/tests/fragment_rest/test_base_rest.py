from time import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.fragment_rest.base_rest import BaseFragmentRest
from src.fragment_rest.models import FragmentSession
from tests.fixtures.random_objects import rstr


@pytest.fixture
def fragment_rest(ton_connect, fragment_session) -> BaseFragmentRest:
    fragment_rest = BaseFragmentRest(ton_connect)

    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._auth = MagicMock(sepc=FragmentRestAuth)
    fragment_rest._session = fragment_session

    return fragment_rest


@pytest.mark.asyncio
async def test_calls_ensure_fresh_session_before_request(
    fragment_rest: BaseFragmentRest,
    mocker: MockerFixture,
    fragment_session: FragmentSession,
) -> None:
    ensure_fresh_session_mock = mocker.patch.object(
        fragment_rest, "ensure_fresh_session", AsyncMock()
    )
    fragment_rest._session = fragment_session

    await fragment_rest._request(method="getSomeThing", data={})

    ensure_fresh_session_mock.assert_called_once()


@pytest.mark.asyncio
async def test_request_raises_if_no_session(fragment_rest: BaseFragmentRest) -> None:
    fragment_rest._session = None

    with pytest.raises(RuntimeError):
        await fragment_rest._request(method="doSomething", data={})


@pytest.mark.asyncio
async def test_ensure_fresh_session_does_not_authorizes_if_last_upd_new(
    fragment_rest: MagicMock,
) -> None:
    fragment_rest._auth = MagicMock(spec=FragmentRestAuth)
    fragment_rest._session.last_session_check = (
        time() + fragment_rest.SESSION_CHECK_DELTA
    )

    await fragment_rest.ensure_fresh_session()

    fragment_rest._auth.authorize.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_fresh_session_does_not_authorizes_if_last_upd_stale(
    fragment_rest: BaseFragmentRest,
) -> None:
    fragment_rest._auth = MagicMock(spec=FragmentRestAuth)
    fragment_rest._last_session_check = 0

    await fragment_rest.ensure_fresh_session()

    fragment_rest._auth.authorize.assert_called_once()


@pytest.mark.asyncio
async def test_request_returns_data(
    fragment_rest: BaseFragmentRest, fragment_session: FragmentSession
) -> None:
    fragment_rest._auth = MagicMock(spec=FragmentRestAuth)
    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._last_session_check = time() + fragment_rest.SESSION_CHECK_DELTA
    fragment_rest._session = fragment_session

    prepared = {"something": rstr("mooock"), "otherData": "yes"}
    fragment_rest._api.request.return_value = prepared

    data = await fragment_rest._request(method="someMethod", data={})

    fragment_rest._api.request.assert_called_once()
    assert data == prepared

from time import time
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from pytest_mock import MockerFixture

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth
from src.fragment_rest.models import FragmentSession
from src.fragment_rest.rest import FragmentRest


@pytest_asyncio.fixture
async def fragment_rest(ton_connect, mocker: MockerFixture) -> FragmentRest:
    mocker.patch.object(FragmentRest, "_load_session", return_value=None)

    fragment_rest = FragmentRest(ton_connect)

    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._auth = MagicMock(sepc=FragmentRestAuth)
    fragment_rest._last_session_check = time() + fragment_rest.SESSION_LT + 9999

    return fragment_rest


@pytest.mark.asyncio
async def test_calls_ensure_fresh_session_before_request(
    fragment_rest: FragmentRest,
    mocker: MockerFixture,
    fragment_session: FragmentSession,
) -> None:
    refresh_session_mock = mocker.patch.object(
        fragment_rest, "ensure_fresh_session", AsyncMock()
    )
    fragment_rest._session = fragment_session

    await fragment_rest._request(method="getSomeThing", data={})

    refresh_session_mock.assert_called_once()


@pytest.mark.asyncio
async def test_request_raises_if_no_session(fragment_rest: FragmentRest) -> None:
    fragment_rest._session = None

    with pytest.raises(RuntimeError):
        await fragment_rest._request(method="doSomething", data={})


@pytest.mark.asyncio
async def test_request_calls_api_request_with_right_session_data(
    fragment_rest: FragmentRest, fragment_session: FragmentSession
) -> None:
    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._session = fragment_session

    await fragment_rest._request(method="someMethod", data={"fruit": "apelsin"})

    fragment_rest._api.request.assert_called_once_with(
        hash=fragment_session.hash,
        method="someMethod",
        data={"fruit": "apelsin"},
        cookies=fragment_session.cookies,
    )


@pytest.mark.asyncio
async def test_ensure_fresh_session_does_not_authorizes_if_last_upd_new(
    fragment_rest: FragmentRest, mocker: MockerFixture
) -> None:
    fragment_rest._auth = MagicMock(spec=FragmentRestAuth)
    fragment_rest._last_session_check = time() + fragment_rest.SESSION_LT

    await fragment_rest.ensure_fresh_session()

    fragment_rest._auth.authorize.assert_not_called()


@pytest.mark.asyncio
async def test_ensure_fresh_session_does_not_authorizes_if_last_upd_stale(
    fragment_rest: FragmentRest, mocker: MockerFixture
) -> None:
    fragment_rest._auth = MagicMock(spec=FragmentRestAuth)
    fragment_rest._last_session_check = 0

    await fragment_rest.ensure_fresh_session()

    fragment_rest._auth.authorize.assert_called_once()


@pytest.mark.asyncio
async def test_search_stars_recipient_raises_below_50(
    fragment_rest: FragmentRest,
) -> None:
    pass


@pytest.mark.asyncio
async def test_search_stars_recipient_raises_bigger_10_000_000(
    fragment_rest: FragmentRest,
) -> None:
    pass


@pytest.mark.asyncio
@pytest.mark.parametrize("amount", [50, 51, 100, 9_999_999])
async def test_different_amounts(fragment_rest: FragmentRest, amount: int) -> None:
    pass

from time import time
from unittest.mock import MagicMock

import pytest
from src.fragment_rest.rest import FragmentRest

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.auth import FragmentRestAuth


@pytest.fixture
def fragment_rest(ton_connect) -> FragmentRest:
    fragment_rest = FragmentRest(ton_connect)

    fragment_rest._api = MagicMock(spec=FragmentAPIClient)
    fragment_rest._auth = MagicMock(sepc=FragmentRestAuth)
    fragment_rest._last_session_check = time() + fragment_rest.SESSION_LT + 9999

    return fragment_rest


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

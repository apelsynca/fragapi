from unittest.mock import MagicMock

import pytest

from src.fragment_rest.rest import FragmentRest


@pytest.fixture
def fragment_rest(ton_connect) -> FragmentRest:
    fragment_rest = FragmentRest(ton_connect)

    fragment_rest._api = MagicMock()
    fragment_rest._auth = MagicMock()

    return fragment_rest


@pytest.mark.asyncio
async def test_search_stars_recipient_below_50() -> None:
    pass


@pytest.mark.asyncio
async def test_search_stars_recipient_bigger_10_000_000() -> None:
    pass


@pytest.mark.asyncio
@pytest.mark.parametrize("amount", [50, 51, 100, 9_999_999])
async def test_different_amounts(amount: int) -> None:
    pass

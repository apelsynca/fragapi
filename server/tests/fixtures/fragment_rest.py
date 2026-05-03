from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from src.fragment_rest.main import FragmentRest


@pytest.fixture
def fragment_rest() -> FragmentRest:
    fragment_rest = MagicMock(spec=FragmentRest)
    client_mock = MagicMock(spec=AsyncClient)
    fragment_rest.client.return_value = client_mock

    return fragment_rest

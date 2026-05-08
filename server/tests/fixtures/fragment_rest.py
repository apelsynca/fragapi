from unittest.mock import MagicMock

import pytest

from src.fragment_rest.rest import FragmentRest


@pytest.fixture
def fragment_rest() -> FragmentRest:
    return MagicMock(spec=FragmentRest)

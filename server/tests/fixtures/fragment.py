from unittest.mock import MagicMock

import pytest

from src.fragment import Fragment


@pytest.fixture
def fragment() -> MagicMock:
    return MagicMock(spec=Fragment)

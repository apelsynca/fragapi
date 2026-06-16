from unittest.mock import MagicMock

import pytest

from src.integrations.fragment import Fragment


@pytest.fixture
def fragment() -> MagicMock:
    return MagicMock(spec=Fragment)

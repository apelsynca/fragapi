from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.fragment_rest.main import FragmentRest


@pytest.fixture(autouse=True)
def fragment_request(mocker: MockerFixture, fragment_rest: FragmentRest) -> MagicMock:
    mocker.patch("src.fragment_rest.fragment_rest.authorize")
    return mocker.patch("src.fragment.rest.fragment_rest.request")

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def fragment_request(mocker: MockerFixture) -> MagicMock:
    mocker.patch("src.fragment_rest.fragment_rest.authorize")
    return mocker.patch("src.fragment.rest.fragment_rest.request")

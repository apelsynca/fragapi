from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.payment.service import PaymentService


@pytest.fixture(autouse=True)
def payment_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.tonapi.service.payment_service", spec=PaymentService)

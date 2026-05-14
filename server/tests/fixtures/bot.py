from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from telegram.ext import Application, ExtBot


@pytest.fixture(autouse=True)
def bot_application(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("src.bot.get_bot_application", spec=Application)
    mock.bot = MagicMock(spec=ExtBot)

    return mock


@pytest.fixture(autouse=True)
def bot(bot_application: Application) -> ExtBot:
    return bot_application.bot

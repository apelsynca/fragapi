import logging

from tests.fixtures.auth import *  # noqa: F403
from tests.fixtures.base import *  # noqa: F403
from tests.fixtures.database import *  # noqa: F403
from tests.fixtures.fragment import *  # noqa: F403
from tests.fixtures.random_objects import *  # noqa: F403
from tests.fixtures.redis import *  # noqa: F403
from tests.fixtures.ton_connect import *  # noqa: F403
from tests.fixtures.worker import *  # noqa: F403

# Quiet down external libraries during testing
logging.getLogger("asyncio").setLevel(logging.INFO)

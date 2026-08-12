import logging

from tests.fixtures.auth import *
from tests.fixtures.base import *
from tests.fixtures.database import *
from tests.fixtures.fragment import *
from tests.fixtures.random_objects import *
from tests.fixtures.redis import *
from tests.fixtures.ton_connect import *
from tests.fixtures.worker import *

# Quiet down external libraries during testing
logging.getLogger("asyncio").setLevel(logging.INFO)

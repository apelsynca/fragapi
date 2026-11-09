from collections.abc import AsyncGenerator
from typing import Annotated

import structlog
from taskiq import Context, TaskiqDepends, TaskiqEvents, TaskiqState

from src.integrations.fragment import Fragment
from src.integrations.fragment.rest_client import FragmentRestClient
from src.kit.ton_connect import TonConnect
from src.logging import Logger
from src.wallet.ton import create_wallet
from src.worker import broker

log: Logger = structlog.get_logger()


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def create_fragment(state: TaskiqState) -> None:
    # Own login and session file (FRAG_FRAGMENT_SESSION_PATH), separate from the app's.
    ton_connect = TonConnect.from_wallet(
        wallet=create_wallet(), tc_domain="fragment.com"
    )
    client = FragmentRestClient(ton_connect=ton_connect)
    await client.ensure_authorized()
    state.fragment = Fragment(clients=[client])
    log.info("Created Fragment")


async def get_fragment(
    context: Annotated[Context, TaskiqDepends()],
) -> AsyncGenerator[Fragment]:
    try:
        fragment: Fragment = context.state.fragment
    except AttributeError as e:
        raise RuntimeError(
            "Fragment is not present in the context state. "
            "Did you (re)moved broker events?"
        ) from e

    yield fragment

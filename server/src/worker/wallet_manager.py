from collections.abc import AsyncGenerator
from typing import Annotated

import structlog
from taskiq import Context, TaskiqDepends, TaskiqEvents, TaskiqState

from src.integrations.ton_wallet.manager import WalletManager
from src.logging import Logger
from src.wallet.ton import create_wallet
from src.wallet.ton import toncenter as toncenter_client
from src.worker import broker

log: Logger = structlog.get_logger()


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def create_wallet_manager(state: TaskiqState):
    wallet = create_wallet()  # for now
    state.wallet_manager = WalletManager(wallet=wallet)
    log.info("Created WalletManager")


# NOTE: can be moved as get_wallet (manager logic outside)
async def get_wallet_manager(
    context: Annotated[Context, TaskiqDepends()],
) -> AsyncGenerator[WalletManager]:
    try:
        wallet_manager: WalletManager = context.state.wallet_manager
    except AttributeError as e:
        raise RuntimeError(
            "WalletManager is not present in the context state. "
            "Did you (re)moved broker events?"
        ) from e

    async with toncenter_client:
        yield wallet_manager

import asyncio

from src.integrations.fragment import Fragment
from src.integrations.fragment.rest_client import FragmentRestClient
from src.kit.ton_connect import TonConnect
from src.wallet.ton import create_wallet


async def main() -> None:
    """
    If there is no session present -> Authorizes and saves it.
    If there is a session present -> just acts on it.
    """

    wallet = create_wallet()
    ton_connect = TonConnect(wallet=wallet, tc_domain="fragment.com")
    client = FragmentRestClient(ton_connect=ton_connect, session_key="first")

    await client.ensure_authorized()

    fragment = Fragment(clients=[client])

    await asyncio.sleep(1.2)

    data = await fragment.search_stars_recipient(query="homocitrus", quantity=None)
    print(data)


if __name__ == "__main__":
    asyncio.run(main())

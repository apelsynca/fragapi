import asyncio

from src.fragment_rest.exceptions import FragmentAPIAccessDenied
from src.fragment_rest.rest import FragmentRest
from src.kit.ton_connect import TonConnect
from src.wallet.ton import create_wallet


def main():
    wallet = create_wallet()

    ton_connect = TonConnect(wallet=wallet, tc_domain="fragment.com")
    fragment_rest = FragmentRest(ton_connect=ton_connect)

    asyncio.run(do_work(fragment_rest))


async def do_work(fragment_rest: FragmentRest) -> None:
    await fragment_rest.start()

    recipient_data = await fragment_rest.search_stars_recipient(
        query="apelsynca", quantity=50
    )

    print(recipient_data)

    try:
        buy_request = await fragment_rest.init_buy_stars_request(
            recipient=recipient_data.found.recipient, quantity=50
        )
        print(buy_request)
    except FragmentAPIAccessDenied:
        print("Probably no KYC, access denied")


if __name__ == "__main__":
    main()

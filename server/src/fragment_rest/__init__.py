from fastapi import Request
from tonutils.contracts import WalletV5R1

from src.fragment_rest.rest import FragmentRest
from src.kit.ton_connect import TonConnect


def create_fragment_rest(wallet: WalletV5R1) -> FragmentRest:
    fragment_ton_connect = TonConnect(wallet, tc_domain="fragment.com")

    return FragmentRest(fragment_ton_connect)


def get_fragment_rest(request: Request) -> FragmentRest:
    return request.state.fragment_rest

from fastapi import Request

from src.fragment_rest.rest import FragmentRest
from src.kit.ton_connect import TonConnect


def create_fragment_rest(ton_connect: TonConnect) -> FragmentRest:
    return FragmentRest(ton_connect)


def get_fragment_rest(request: Request) -> FragmentRest:
    return request.state.fragment_rest

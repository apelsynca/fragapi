from fastapi import FastAPI

from src.fragment_rest.main import FragmentRest


def get_fragment_rest(request: FastAPI) -> FragmentRest:
    return request.state.fragment_rest

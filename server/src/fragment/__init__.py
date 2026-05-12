from fastapi import Request

from src.fragment.main import Fragment


def get_fragment(request: Request) -> Fragment:
    return request.state.fragment


__all__ = ["Fragment"]

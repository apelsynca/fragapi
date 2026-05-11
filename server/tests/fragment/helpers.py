import json
from typing import Any

from src.fragment.rest_request import BaseRequest


class MockRequest(BaseRequest):
    def __init__(
        self,
        return_status_code: int = 404,
        return_json: Any | None = None,
        return_text: Any | None = None,
        return_cookies: dict[str, str] = {},
    ) -> None:
        self.return_status_code = return_status_code
        self.return_json = return_json
        self.return_text = return_text
        self.return_cookies = return_cookies

    async def do_request(
        self,
        url: str,
        method: str,
        json_data: dict | None = None,
        *,
        cookies: dict[str, str] | None = None,
    ) -> tuple[int, bytes, dict[str, str]]:
        if self.return_json and self.return_text:
            raise RuntimeError("Cannot do both self.return_json and self.return_text")

        content = b""
        if self.return_json:
            content = json.dumps(self.return_json).encode("utf-8")
        if self.return_text:
            content = self.return_text.encode("utf-8")

        return (
            self.return_status_code,
            content,
            self.return_cookies,
        )

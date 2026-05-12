import json
from typing import Any

from src.fragment.rest_request import BaseClient, FragCookies


class MockClient(BaseClient):
    def __init__(
        self,
        return_status_code: int = 404,
        return_json: Any | None = None,
        return_text: Any | None = None,
        saved_cookies: dict[str, str] = {},
    ) -> None:
        self.return_status_code = return_status_code
        self.return_json = return_json
        self.return_text = return_text
        self.saved_cookies = saved_cookies

    async def do_request(
        self,
        url: str,
        method: str,
        form_data: dict | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, bytes]:
        if self.return_json and self.return_text:
            raise RuntimeError("Cannot do both self.return_json and self.return_text")

        content = b""
        if self.return_json:
            content = json.dumps(self.return_json).encode("utf-8")
        if self.return_text:
            content = self.return_text.encode("utf-8")

        return self.return_status_code, content

    def extract_cookies(self) -> FragCookies:
        return self.saved_cookies

import json
import re
from time import time

from src.fragment.exceptions import (
    FragmentAPIAccessDenied,
    FragmentAPIError,
    FragmentAPIUsersNotFound,
    FragmentError,
)
from src.fragment.rest_request import BaseRequest, HttpxRequest
from src.fragment.session_storage import SessionStorage
from src.fragment.types import MainPageTokens
from src.kit.ton_connect import TonConnect

FragCookie = dict[str, str]


class FragmentRestClient:
    STALE_TIME = 60 * 30  # 30 minutes

    def __init__(self, ton_connect: TonConnect, session_key: str) -> None:
        self.session_storage = SessionStorage(session_key=session_key)
        self.session_storage.load_session()  # fails only if file does not exists (AND THE TESTS FOR THAT IS GOING FOR IT, NOT FOR HERE)

        self._request: BaseRequest = HttpxRequest()

        self._ton_connect = ton_connect
        self.last_session_check: float = 0

    async def api_request(self, method: str, data: dict[str, str]) -> None:
        if data.get("method", None) is not None:
            raise ValueError("Cannot include key method in api_request.data")
        data["method"] = method

        if self.session_storage.session is None:
            raise FragmentError()

        now = time()
        if (
            self.session_storage.session is not None
            and now - self.STALE_TIME > self.last_session_check
        ):
            await self._check_session()

        status_code, content, _ = await self._request.do_request(
            url=f"https://fragment.com/api?hash={self.session_storage.session.hash}",
            method="POST",
            json_data=data,
        )

        if status_code != 200:
            raise FragmentError(f"Status - {status_code}")

        response_data = json.loads(content)

        if "error" in response_data:
            if "no telegram users found" in response_data["error"].lower():
                raise FragmentAPIUsersNotFound(response_data["error"])
            if "access denied" in response_data["error"].lower():
                raise FragmentAPIAccessDenied(response_data["error"])
            raise FragmentAPIError(response_data["error"])

        return response_data

    async def _check_session(self) -> None:
        if self.session_storage.session is None:
            await self._authorize()
        else:
            await self._ensure_correct_session_tokens()

    async def _authorize(self) -> None:
        pass

    async def _ensure_correct_session_tokens(self) -> None:
        pass

    async def get_main_page(self) -> tuple[MainPageTokens, FragCookie]:
        request_cookies = (
            None
            if self.session_storage.session is None
            else self.session_storage.session.cookies
        )

        status_code, content, response_cookies = await self._request.do_request(
            url="https://fragment.com/", method="GET", cookies=request_cookies
        )
        text = content.decode("utf-8")

        if status_code != 200:
            raise FragmentError("Main page unavailable")

        session_hash_match = re.search(r'"apiUrl":"\\/api\?hash=(\w+)"', text)
        if session_hash_match is None:
            raise FragmentError("No session hash match")
        session_hash = session_hash_match.group(1)

        ton_proof_match = re.search(r'"ton_proof":"(.+?)"', text)
        if ton_proof_match is None:
            raise FragmentError("No ton proof match")
        session_ton_proof = ton_proof_match.group(1)

        ton_rate_match = re.search(r'"tonRate":(\d+.?\d+)', text)
        if ton_rate_match is None:
            raise FragmentError("No ton rate")
        ton_rate_match = float(ton_rate_match.group(1))

        return MainPageTokens(
            hash=session_hash,
            ton_proof_payload=session_ton_proof,
            ton_rate=ton_rate_match,
        ), response_cookies

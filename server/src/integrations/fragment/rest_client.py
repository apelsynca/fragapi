import asyncio
import json
import re
from time import time
from typing import Any

from src.integrations.fragment.exceptions import (
    FragmentAPIAccessDenied,
    FragmentAPIError,
    FragmentAPINotAUser,
    FragmentAPIUsersNotFound,
    FragmentError,
)
from src.integrations.fragment.models import MainPageTokens
from src.integrations.fragment.rest_request import BaseClient, HttpxClient
from src.integrations.fragment.session_storage import SessionStorage
from src.kit.ton_connect import TonConnect


class FragmentRestClient:
    DOMAIN = "fragment.com"
    STALE_TIME = 60 * 30  # 30 minutes

    def __init__(self, ton_connect: TonConnect, session_key: str) -> None:
        if ton_connect.tc_domain != self.DOMAIN:
            raise RuntimeError(
                f"ton_connect.tc_domain is different from required {self.DOMAIN}."
            )

        self.session_storage = SessionStorage(session_key=session_key)
        self.session_storage.load()  # fails only if file does not exists

        self._client: BaseClient = HttpxClient(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/150.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Host": self.DOMAIN,
            },
            http2=True,
            cookies=self.session_storage.session.cookies
            if self.session_storage.session
            else None,
        )

        self._ton_connect = ton_connect
        self.last_session_check: float = 0

    async def api_request(self, method: str, data: dict[str, str]) -> Any:
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
            await self.ensure_authorized()

        status_code, content = await self._client.do_request(
            url=f"https://fragment.com/api?hash={self.session_storage.session.hash}",
            method="POST",
            form_data=data,
            headers={"X-Requested-With": "XMLHttpRequest"},
        )

        if status_code != 200:
            raise FragmentError(f"Status - {status_code}")

        response_data = json.loads(content)

        self._validate_response_json(data=response_data)

        return response_data

    def _validate_response_json(self, data: dict) -> None:
        if "error" not in data:
            return

        error_text = data["error"]
        error_lowered = error_text.lower()

        if "no telegram users found" in error_lowered:
            raise FragmentAPIUsersNotFound(error_text)
        if "access denied" in error_lowered:
            raise FragmentAPIAccessDenied(error_text)
        if "enter a username assigned to a user" in error_lowered:
            raise FragmentAPINotAUser(error_text)

        raise FragmentAPIError(error_text)

    async def ensure_authorized(self) -> None:
        if self.session_storage.session is None:
            await self.authorize()
        else:
            is_correct = await self._is_correct_session_tokens()
            if not is_correct:
                await self.authorize()

    async def authorize(self) -> None:
        """
        Clears all of the current data and authorizes again via TonConnect
        """

        main_page_tokens = await self.get_main_page_tokens()
        self.session_storage.save_tokens(main_page_tokens)

        await asyncio.sleep(0.5)
        await self.check_ton_proof_auth()

        self.session_storage.save_cookies(self._client.extract_cookies())
        self.session_storage.save()

    async def _is_correct_session_tokens(self) -> bool:
        if self.session_storage.session is None:
            raise ValueError("Session must not be None")

        session = self.session_storage.session

        main_page_tokens = await self.get_main_page_tokens()
        if main_page_tokens.hash != session.hash:
            return False
        if main_page_tokens.ton_proof_payload != session.ton_proof_payload:
            return False

        return True

    async def get_main_page_tokens(self) -> MainPageTokens:
        status_code, content = await self._client.do_request(
            url="https://fragment.com/", method="GET"
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
        )

    async def check_ton_proof_auth(self) -> tuple[bool]:
        if self.session_storage.session is None:
            raise RuntimeError("No session while checking ton proof auth")

        data = self._ton_connect.get_connect_json_data(
            ton_proof_payload=self.session_storage.session.ton_proof_payload
        )
        response_data = await self.api_request(
            method="checkTonProofAuth",
            data=data,
        )

        return response_data["verified"]

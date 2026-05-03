import re

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.exceptions import FragmentAPIBadRequest, FragmentAuthError
from src.fragment_rest.models import FragmentSession
from src.kit.ton_connect import TonConnect


class FragmentRestAuth:
    def __init__(self, ton_connect: TonConnect) -> None:
        self._tc = ton_connect

        self.has_authorized: bool = False

    async def authorize(self) -> None:
        self.load_session()

    async def get_online_session(
        self, api_client: FragmentAPIClient
    ) -> FragmentSession:
        response_text = await api_client.get_main_page()

        session_hash_match = re.search(r'"apiUrl":"\\/api\?hash=(\w+)"', response_text)
        if session_hash_match is None:
            raise FragmentAuthError("No session hash match")
        session_hash = session_hash_match.group(1)

        ton_proof_match = re.search(r'"ton_proof":"(.+?)"', response_text)
        if ton_proof_match is None:
            raise FragmentAuthError("No ton proof match")
        session_ton_proof = ton_proof_match.group(1)

        return FragmentSession(
            hash=session_hash,
            ton_proof_payload=session_ton_proof,
            cookies={},
        )

    def load_session(self) -> FragmentSession | None:
        return None

    async def check_session(
        self, api_client: FragmentAPIClient, session: FragmentSession
    ) -> bool:
        if self.has_authorized is False:
            return False

        data = self._tc.get_connect_request_data(
            ton_proof_payload=session.ton_proof_payload
        )

        headers = {"X-Requested-With": "XMLHttpRequest"}

        try:
            auth_data = await api_client.request(
                method="checkTonProofAuth",
                data=data.model_dump(),
                headers=headers,
                check_authorized=False,
            )
        except FragmentAPIBadRequest:
            return False

        if verified := auth_data.get("verified", False):
            return verified
        return False

import re

from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.exceptions import FragmentAPIBadRequest, FragmentAuthError
from src.fragment_rest.models import FragmentSession
from src.kit.ton_connect import TonConnect


class FragmentRestAuth:
    TC_DOMAIN = "fragment.com"

    def __init__(self, ton_connect: TonConnect) -> None:
        if ton_connect.tc_domain != self.TC_DOMAIN:
            raise RuntimeError(
                f"ton_connect.tc_domain is different from required {self.TC_DOMAIN}."
            )

        self.ton_connect = ton_connect

    async def authorize(self, api_client: FragmentAPIClient) -> FragmentSession:
        not_authed_session = await self.get_online_session(api_client)
        await self.check_session(api_client, not_authed_session)
        authed_session = await self.get_online_session(api_client)

        return authed_session

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
            cookies=api_client.get_client_relevant_cookies(),
        )

    async def check_session(
        self, api_client: FragmentAPIClient, session: FragmentSession
    ) -> bool:
        data = self.ton_connect.get_connect_request_data(
            ton_proof_payload=session.ton_proof_payload
        )

        headers = {"X-Requested-With": "XMLHttpRequest"}

        try:
            auth_data = await api_client.request(
                hash=session.hash,
                method="checkTonProofAuth",
                data=data.model_dump(),
                headers=headers,
                # cookies
            )
        except FragmentAPIBadRequest:
            return False

        if verified := auth_data.get("verified", False):
            return verified
        return False

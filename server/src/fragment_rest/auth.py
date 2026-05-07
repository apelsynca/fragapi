from src.fragment_rest.api import FragmentAPIClient
from src.fragment_rest.exceptions import FragmentAPIBadRequest
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
        main_page_tokens = await api_client.get_main_page_tokens()

        return FragmentSession(
            hash=main_page_tokens.hash,
            ton_proof_payload=main_page_tokens.ton_proof_payload,
            cookies=api_client.get_client_relevant_cookies(),
        )

    async def check_session(
        self, api_client: FragmentAPIClient, session: FragmentSession
    ) -> bool:
        ton_connect_data = self.ton_connect.get_connect_json_data(
            ton_proof_payload=session.ton_proof_payload
        )

        try:
            auth_data = await api_client.request(
                hash=session.hash,
                method="checkTonProofAuth",
                data=ton_connect_data,
                cookies=session.cookies,
            )
        except FragmentAPIBadRequest:
            return False

        if verified := auth_data.get("verified", False):
            return verified
        return False

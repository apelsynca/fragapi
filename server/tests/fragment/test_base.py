import pytest

from src.fragment_rest.exceptions import FragmentUserNotFound
from src.fragment_rest.main import FragmentRest


@pytest.mark.asyncio
async def test_request_raises_not_found_if_stars_recipient_not_found(
    fragment_rest: FragmentRest,
) -> None:
    # fragment_client_mock.return_value = {"error": "No Telegram users found."}

    with pytest.raises(FragmentUserNotFound):
        await fragment_rest.request(
            method="searchStarsRecipient", data={"query": "anything", "quantity": "50"}
        )

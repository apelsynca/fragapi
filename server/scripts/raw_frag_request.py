import asyncio

import httpx

HASH = "ce7de406bde4540cfc"
STEL_SSID = "xxx"
STEL_TOKEN = "xxx"
STEL_TON_TOKEN = "xxx"


async def main():
    client = httpx.AsyncClient(
        http2=True,
        headers={
            "Origin": "https://fragment.com",
            "Referer": "https://fragment.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
        },
        cookies={"stel_dt": "-180"},
    )

    async with client as client:
        response = await client.post(
            url=f"https://fragment.com/api?hash={HASH}",
            data={
                "query": "homocitrus",
                "quantity": "",
                "method": "searchStarsRecipient",
            },
            cookies={
                "stel_dt": "-180",
                "stel_ssid": STEL_SSID,
                "stel_token": STEL_TOKEN,
                "stel_ton_token": STEL_TON_TOKEN,
            },
            headers={
                "Host": "fragment.com",
                "Referer": "https://fragment.com/stars/buy?quantity=50",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        print(response.status_code, response.content)


if __name__ == "__main__":
    asyncio.run(main())

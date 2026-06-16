import asyncio

import httpx

HASH = input("Hash: ")
STEL_SSID = input("SSID: ")
STEL_TOKEN = input("TOKEN: ")
STEL_TON_TOKEN = input("TON TOKEN: ")


async def main():
    client = httpx.AsyncClient(
        http2=True,
        headers={
            "Origin": "https://fragment.com",
            "Referer": "https://fragment.com/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/150.0",
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
                "quantity": "52",
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
        json = response.json()

        if response.status_code != 200:
            print(response.status_code, json)

        recipient = json["found"]["recipient"]
        print(recipient)

        response = await client.post(
            url=f"https://fragment.com/api?hash={HASH}",
            data={
                "recipient": recipient,
                "quantity": "52",
                "payment_method": "ton",
                "method": "initBuyStarsRequest",
            },
            cookies={
                "stel_dt": "-180",
                "stel_ssid": STEL_SSID,
                "stel_token": STEL_TOKEN,
                "stel_ton_token": STEL_TON_TOKEN,
            },
            headers={
                "Host": "fragment.com",
                "X-Requested-With": "XMLHttpRequest",
            },
        )

        print(response.status_code, "Status for Buy")
        json = response.json()

        print(json)


if __name__ == "__main__":
    asyncio.run(main())

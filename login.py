import asyncio
from ewelink import EWeLink


APP_ID = "0ygkstU1AovdDXtI65mok181GCCY87EF"
APP_SECRET = "0UZMVs2oaSoFiYcqtDM88hOTFLgLpZXu"
EMAIL = "mattia.millebolle@gmail.com"
PASSWORD = "Millebolle.1"

async def main():
    client = EWeLink(
        appid=APP_ID,
        appsecret=APP_SECRET,
        region="eu"
    )

    await client.login(EMAIL, PASSWORD)

    devices = await client.get_devices()
    for d in devices:
        print(d["name"], d["deviceid"])

asyncio.run(main())

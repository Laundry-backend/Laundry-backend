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

    result = await client.login(EMAIL, PASSWORD)
    print("LOGIN OK:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

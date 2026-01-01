import asyncio
from ewelink import EWeLink

EMAIL = "mattia.millebolle@gmail.com"
PASSWORD = "Millebolle.1"
REGION = "eu"

async def main():
    client = EWeLink(EMAIL, PASSWORD, REGION)
    result = await client.login()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

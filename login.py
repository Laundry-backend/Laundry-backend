import asyncio
from ewelink import EWeLink

EMAIL = "mattia.millebolle@gmail.com"
PASSWORD = "Millebolle.1"

async def main():
    client = EWeLink()  # 👈 NIENTE parametri qui

    result = await client.login(
        email=EMAIL,
        password=PASSWORD,
        region="eu"
    )

    print("LOGIN OK")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

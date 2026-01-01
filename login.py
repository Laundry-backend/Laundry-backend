import asyncio
from ewelink import EWeLink

EMAIL = "mattia.millebolle@gmail.com"
PASSWORD = "Millebolle.1"
REGION = "eu"  # Europa

async def main():
    client = EWeLink(
        email=EMAIL,
        password=PASSWORD,
        region=REGION
    )

    await client.login()

    devices = await client.get_devices()
    print("Dispositivi trovati:")
    for d in devices:
        print(f"- {d['name']} | id: {d['deviceid']} | online: {d['online']}")

asyncio.run(main())

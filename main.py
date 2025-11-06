import asyncio
from orange_api import *


async def main():
    try:
        phone_number = "+99012345678"
        print(await verify_device_location_by_city(
            phone_number=phone_number,
            city="Sibiu",
            country="Romania",
            radius=5000
        ))


    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    


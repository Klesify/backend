import asyncio
from auth import get_access_token


async def main():
    try:
        print("Fetching OAuth token...")
        token = await get_access_token()
        print(f"Token: {token}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    


import asyncio
from auth import get_access_token
from sym_swap import check_sim_swap, retrieve_sim_swap_date


async def main():
    try:
        phone_number = "+99012345678"  # Replace with actual number
        
        print(f"Checking SIM swap status for {phone_number}...")
        result = await check_sim_swap(phone_number)
        result2 = await retrieve_sim_swap_date(phone_number)
            
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    


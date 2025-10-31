import asyncio
from auth import get_access_token
from sym_swap import check_sim_swap


async def main():
    try:
        # Example: Check if a phone number was SIM swapped
        phone_number = "+99012345678"  # Replace with actual number
        
        print(f"Checking SIM swap status for {phone_number}...")
        result = await check_sim_swap(phone_number)
        
        if result["status"] == "success":
            if result["swapped"]:
                print(f"⚠️  WARNING: Phone number {phone_number} was recently SIM swapped!")
            else:
                print(f"✓ Phone number {phone_number} has NOT been SIM swapped.")
        else:
            print(f"✗ Check failed: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    


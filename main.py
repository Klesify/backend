import asyncio
from auth import get_access_token
from sym_swap import check_sim_swap, retrieve_sim_swap_date
from kyc_match import match_customer_data
from geocoding import get_city_coordinates
import location_verification


async def main():
    try:
        phone_number = "+99012345678"  # Replace with actual number
        print(await location_verification.verify_device_location_by_city(phone_number=phone_number, city="Avrig"))
        
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    


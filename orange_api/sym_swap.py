from typing import Optional
import httpx
from .auth import get_access_token


async def check_sim_swap(phone_number: str, max_age: Optional[int] = None):
    """
    Check if a SIM swap has occurred for the given phone number.
    
    Args:
        phone_number (str): The phone number to check.
        max_age (int, optional): Maximum age of SIM swap data in hours. Defaults to 240 (10 days). Max value is 2400.
    
    Returns:
        dict: Result of the SIM swap check
            - swapped (bool): True if a SIM swap has occurred during the checked period, False otherwise
    """
    # Validate max_age if provided
    if max_age is not None:
        if not isinstance(max_age, int) or max_age < 1 or max_age > 2400:
            raise ValueError("max_age must be between 1 and 2400 hours")
    
    # Get valid OAuth token
    token = await get_access_token()
    
    # API endpoint
    url = "https://api.orange.com/camara/playground/api/sim-swap/v1/check"
    
    # Request payload
    if (max_age is None):
        data = {
            "phoneNumber": phone_number
        }
    else:
        data = {
            "phoneNumber": phone_number,
            "maxAge": max_age
        }
    
    # Headers with Bearer token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"SIM swap check for {phone_number}: swapped={result.get('swapped')}")
            
            return {
                "swapped": result.get("swapped", False),
                "phone_number": phone_number,
                "status": "success"
            }
            
    except httpx.HTTPStatusError as e:
        print(f"SIM swap check failed with status {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return {
            "error": f"API error: {e.response.status_code}",
            "details": e.response.text,
            "status": "failed"
        }
    except Exception as e:
        print(f"SIM swap check failed: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }


async def retrieve_sim_swap_date(phone_number: str, x_correlator: Optional[str] = None) -> dict:
    """
    Retrieve the date of the latest SIM swap for the given phone number.
    
    Args:
        phone_number (str): The phone number to check.

    Returns:
        dict: Result containing the latest SIM swap date
            - latestSimChange (str): Date of the latest SIM swap in ISO 8601 format (ex: 2024-12-03T08:30:00.000Z)
    """
    # Get valid OAuth token
    token = await get_access_token()
    
    # API endpoint
    url = "https://api.orange.com/camara/playground/api/sim-swap/v1/retrieve-date"
    
    # Request payload (JSON format for this endpoint)
    payload = {
        "phoneNumber": phone_number
    }
    
    # Headers with Bearer token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,  # Use json parameter for application/json
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            latest_change = result.get("latestSimChange")
            
            print(f"SIM swap date for {phone_number}: {latest_change}")
            
            return {
                "latestSimChange": latest_change,
                "phone_number": phone_number,
                "status": "success"
            }
            
    except httpx.HTTPStatusError as e:
        print(f"Retrieve SIM swap date failed with status {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return {
            "error": f"API error: {e.response.status_code}",
            "details": e.response.text,
            "status": "failed"
        }
    except Exception as e:
        print(f"✗ Retrieve SIM swap date failed: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }

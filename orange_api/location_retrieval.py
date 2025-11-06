from typing import Optional
import httpx
from .auth import get_access_token


async def retrieve_device_location(
    phone_number: str,
    max_age: Optional[int] = None
) -> dict:
    """
    Retrieve the actual location where a device was last seen.
    
    Args:
        phone_number (str): The phone number in E.164 format (e.g., "+99012345678").
        max_age (int, optional): Maximum age of location data in seconds. Defaults to None.
            - None: Accept any age (most reliable for testing)
            - 0: Require fresh/real-time location
            - N: Location must be no older than N seconds
    
    Returns:
        dict: Location retrieval result containing:
            - lastLocationTime (str): ISO 8601 timestamp when device was at this location
            - area (dict): Location area information:
                - areaType (str): "CIRCLE"
                - center (dict): Center point coordinates:
                    - latitude (float): Center latitude
                    - longitude (float): Center longitude
                - radius (int): Accuracy radius in meters
    
    Raises:
        httpx.HTTPError: If the API request fails
    """
    
    # Get valid OAuth token
    token = await get_access_token()
    
    # API endpoint
    url = "https://api.orange.com/camara/playground/api/location-retrieval/v0.3/retrieve"
    
    # Build request payload
    payload = {
        "device": {
            "phoneNumber": phone_number
        }
    }
    
    # Add maxAge if provided
    if max_age is not None:
        payload["maxAge"] = max_age
    
    # Headers with Bearer token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Add metadata
            result["phone_number"] = phone_number
            result["status"] = "success"
            
            return result
            
    except httpx.HTTPStatusError as e:
        return {
            "error": f"API error: {e.response.status_code}",
            "details": e.response.text,
            "status": "failed",
            "phone_number": phone_number
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
            "phone_number": phone_number
        }
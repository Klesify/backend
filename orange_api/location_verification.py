from typing import Optional
import httpx
from .auth import get_access_token


async def verify_device_location(
    phone_number: str,
    latitude: float,
    longitude: float,
    radius: int = 2000,
    max_age: Optional[int] = None
) -> dict:
    """
    Verify if a device is within a specified geographical area defined by a center point (latitude, longitude) and radius.

    Args:
        phone_number (str): The phone number in E.164 format (e.g., "+99012345678").
        latitude (float): The latitude of the center point. Range: -90 to 90.
        longitude (float): The longitude of the center point. Range: -180 to 180.
        radius (int, optional): The radius of the area in meters. Defaults to 2000. Range: 2,000 to 200,000 meters.
        max_age (int, optional): Maximum age of location data in seconds. Defaults to None.

        
    Returns:
        dict: Verification result containing:
            - verificationResult (str): "TRUE", "FALSE", "PARTIAL", or "UNKNOWN"
            - lastLocationTime (str): ISO 8601 timestamp of location data
            - matchRate (int, optional): Match percentage (only if PARTIAL)
    
    Raises:
        ValueError: If latitude, longitude, or radius are out of valid range.
    """
    
    # Validate parameters
    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    
    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude must be between -180 and 180")
    
    if not (2000 <= radius <= 200000):
        raise ValueError("Radius must be between 2,000 and 200,000 meters")
    
    # Get valid OAuth token
    token = await get_access_token()
    
    # API endpoint
    url = "https://api.orange.com/camara/playground/api/location-verification/v1/verify"
    
    # Build request payload
    payload = {
        "device": {
            "phoneNumber": phone_number
        },
        "area": {
            "areaType": "CIRCLE",
            "center": {
                "latitude": latitude,
                "longitude": longitude
            },
            "radius": radius
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


async def verify_device_location_by_city(
    phone_number: str,
    city: str,
    country: Optional[str] = None,
    radius: int = 2000,
    max_age: Optional[int] = None
) -> dict:
    """
    Verify if a device is within a specified city by first geocoding the city name
    
    Args:
        phone_number (str): The phone number in E.164 format (e.g., "+99012345678").
        city (str): The name of the city to verify location against.
        country (str, optional): The country name to refine geocoding. Defaults to None.
        radius (int, optional): The radius of the area in meters. Defaults to 2000. Range: 2,000 to 200,000 meters.
        max_age (int, optional): Maximum age of location data in seconds. Defaults to None.
        
    Returns:
        dict: Verification result from verify_device_location
            - status (str): "success" or "failed"
            - phone_number (str): The phone number being verified
            - city (str): The city being verified against
            - coordinates (dict): The geocoded coordinates of the city
    """

    location = await get_city_coordinates(city, country)
    
    if location["status"] != "success":
        return {
            "error": f"Could not find coordinates for city: {city}",
            "status": "geocoding_failed",
            "phone_number": phone_number
        }
    
    latitude = location["latitude"]
    longitude = location["longitude"]
    
    # Verify device location
    result = await verify_device_location(
        phone_number=phone_number,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        max_age=max_age
    )
    
    # Add city information to result
    if result["status"] == "success":
        result["city"] = city
        result["coordinates"] = {
            "latitude": latitude,
            "longitude": longitude
        }
    
    return result


async def get_city_coordinates(city: str, country: Optional[str] = None) -> dict:
    # Build search query
    query = city
    if country:
        query = f"{city}, {country}"
    
    # Nominatim API (free OpenStreetMap geocoding)
    url = "https://nominatim.openstreetmap.org/search"
    
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    
    headers = {
        "User-Agent": "Klesify-Backend/1.0"  # Required by Nominatim
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            
            results = response.json()
            
            if not results:
                print(f"City not found: {query}")
                return {
                    "error": f"City '{query}' not found",
                    "status": "not_found"
                }
            
            # Get first result
            location = results[0]
            
            result = {
                "latitude": float(location["lat"], ),
                "longitude": float(location["lon"]),
                "city": city,
                "display_name": location.get("display_name", ""),
                "country": location.get("address", {}).get("country", ""),
                "status": "success"
            }
            
            print(f"{city}: ({result['latitude']}, {result['longitude']})")
            
            return result
            
    except httpx.HTTPStatusError as e:
        print(f"Geocoding failed with status {e.response.status_code}")
        return {
            "error": f"API error: {e.response.status_code}",
            "status": "failed"
        }
    except Exception as e:
        print(f"Geocoding failed: {str(e)}")
        return {
            "error": str(e),
            "status": "failed"
        }
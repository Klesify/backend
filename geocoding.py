from typing import Optional
import httpx


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
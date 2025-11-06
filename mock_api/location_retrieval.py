"""
Mock Location Retrieval API - simulates Orange device location retrieval
"""
from typing import Optional
from .data_loader import load_mock_data


async def retrieve_device_location(
    phone_number: str,
    max_age: Optional[int] = None
) -> dict:
    """
    Retrieve the actual location where a device was last seen.
    
    Args:
        phone_number (str): The phone number in E.164 format
        max_age (int, optional): Maximum age of location data in seconds (ignored in mock)
    
    Returns:
        dict: Location retrieval result
            - lastLocationTime (str): ISO 8601 timestamp
            - area (dict): Location area information with center and radius
            - phone_number (str): The phone number checked
            - status (str): "success" or "not_found"
    """
    # Load mock data
    mock_data = load_mock_data(phone_number)
    
    if not mock_data:
        return {
            "error": f"Phone number {phone_number} not found in mock data",
            "status": "not_found",
            "phone_number": phone_number
        }
    
    location_data = mock_data.get('data', {}).get('location', {})
    
    if not location_data.get('available'):
        return {
            "error": "Location data not available for this number",
            "status": "no_data",
            "phone_number": phone_number
        }
    
    # Build response in Orange API format
    result = {
        "lastLocationTime": location_data.get('lastLocationTime'),
        "area": {
            "areaType": "CIRCLE",
            "center": {
                "latitude": location_data.get('latitude'),
                "longitude": location_data.get('longitude')
            },
            "radius": location_data.get('radius', 500)
        },
        "phone_number": phone_number,
        "status": "success"
    }
    
    return result

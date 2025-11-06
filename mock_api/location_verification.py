"""
Mock Location Verification API - simulates Orange device location verification
"""
from typing import Optional
from math import radians, cos, sin, asin, sqrt
from .data_loader import load_mock_data


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r


async def verify_device_location(
    phone_number: str,
    latitude: float,
    longitude: float,
    radius: int = 2000,
    max_age: Optional[int] = None
) -> dict:
    """
    Verify if a device is within a specified geographical area.

    Args:
        phone_number (str): The phone number in E.164 format
        latitude (float): The latitude of the center point
        longitude (float): The longitude of the center point
        radius (int): The radius of the area in meters (default: 2000)
        max_age (int, optional): Maximum age of location data in seconds (ignored in mock)
        
    Returns:
        dict: Verification result
            - verificationResult (str): "TRUE", "FALSE", or "UNKNOWN"
            - lastLocationTime (str): ISO 8601 timestamp
            - matchRate (int, optional): Match percentage if result is PARTIAL
            - phone_number (str): The phone number checked
            - status (str): "success" or "not_found"
    """
    # Validate parameters
    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    
    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude must be between -180 and 180")
    
    if not (2000 <= radius <= 200000):
        raise ValueError("Radius must be between 2,000 and 200,000 meters")
    
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
            "verificationResult": "UNKNOWN",
            "phone_number": phone_number,
            "status": "success",
            "message": "Location data not available"
        }
    
    device_lat = location_data.get('latitude')
    device_lon = location_data.get('longitude')
    device_accuracy = location_data.get('radius', 500)
    last_location_time = location_data.get('lastLocationTime')
    
    # Calculate distance between device and target center
    distance = calculate_distance(device_lat, device_lon, latitude, longitude)
    
    # Determine verification result
    # Account for device accuracy radius when determining if within range
    combined_radius = radius + device_accuracy
    
    if distance <= radius:
        verification_result = "TRUE"
    elif distance <= combined_radius:
        # Partial match - device might be in range considering accuracy
        match_rate = int(100 * (combined_radius - distance) / device_accuracy)
        result = {
            "verificationResult": "PARTIAL",
            "matchRate": max(0, min(100, match_rate)),
            "lastLocationTime": last_location_time,
            "phone_number": phone_number,
            "status": "success",
            "distance_meters": round(distance, 2)
        }
        return result
    else:
        verification_result = "FALSE"
    
    result = {
        "verificationResult": verification_result,
        "lastLocationTime": last_location_time,
        "phone_number": phone_number,
        "status": "success",
        "distance_meters": round(distance, 2)
    }
    
    return result


async def verify_device_location_by_city(
    phone_number: str,
    city: str,
    country: Optional[str] = None,
    radius: int = 2000,
    max_age: Optional[int] = None
) -> dict:
    """
    Verify if a device is within a specified city (simplified mock version)
    
    Args:
        phone_number (str): The phone number in E.164 format
        city (str): The name of the city to verify location against
        country (str, optional): The country name
        radius (int): The radius of the area in meters (default: 2000)
        max_age (int, optional): Maximum age of location data in seconds
        
    Returns:
        dict: Verification result similar to verify_device_location
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
    kyc_data = mock_data.get('data', {}).get('kyc', {})
    
    # Simple city match based on KYC locality data
    stored_locality = kyc_data.get('locality', '').lower()
    stored_country = kyc_data.get('country', '').lower()
    
    city_match = city.lower() in stored_locality or stored_locality in city.lower()
    country_match = True if not country else (country.lower() in stored_country or stored_country in country.lower())
    
    if city_match and country_match:
        verification_result = "TRUE"
    else:
        verification_result = "FALSE"
    
    result = {
        "verificationResult": verification_result,
        "lastLocationTime": location_data.get('lastLocationTime'),
        "phone_number": phone_number,
        "city": city,
        "stored_locality": kyc_data.get('locality'),
        "coordinates": {
            "latitude": location_data.get('latitude'),
            "longitude": location_data.get('longitude')
        },
        "status": "success"
    }
    
    return result

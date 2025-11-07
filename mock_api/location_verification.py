"""
Mock Location Verification API - simulates Orange device location verification
"""
from typing import Optional
from math import radians, cos, sin, asin, sqrt
from .data_loader import load_user_data


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
    Verify if a device is within a specified geographical area and return scam score.

    Args:
        phone_number (str): The phone number in E.164 format
        latitude (float): The latitude of the center point
        longitude (float): The longitude of the center point
        radius (int): The radius of the area in meters (default: 2000)
        max_age (int, optional): Maximum age of location data in seconds (ignored in mock)
        
    Returns:
        dict: Verification result with scam score
            - scamScore (int): Score from 1-100 (higher = more likely scam)
            - verificationResult (str): "MATCH", "NO_MATCH", or "UNKNOWN"
            - lastLocationTime (str): ISO 8601 timestamp
            - distance_meters (float): Distance between device and target
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
    mock_data = load_user_data(phone_number)
    
    if not mock_data:
        return {
            "error": f"Phone number {phone_number} not found in mock data",
            "status": "not_found",
            "phone_number": phone_number,
            "scamScore": 95  # High score if user not found
        }
    
    location_data = mock_data.get('data', {}).get('location', {})
    
    if not location_data.get('available'):
        return {
            "verificationResult": "UNKNOWN",
            "phone_number": phone_number,
            "status": "success",
            "scamScore": 75,  # High score if location unavailable
            "message": "Location data not available"
        }
    
    device_lat = location_data.get('latitude')
    device_lon = location_data.get('longitude')
    device_accuracy = location_data.get('radius', 500)
    last_location_time = location_data.get('lastLocationTime')
    
    # Calculate distance between device and target center
    distance = calculate_distance(device_lat, device_lon, latitude, longitude)
    
    # Calculate scam score based on distance
    combined_radius = radius + device_accuracy
    
    if distance <= radius:
        # Perfect match - very low scam probability
        verification_result = "MATCH"
        scam_score = max(1, int(5 + (distance / radius) * 10))  # 1-15 range
    elif distance <= combined_radius:
        # Partial match - moderate scam probability
        verification_result = "PARTIAL_MATCH"
        match_percentage = (combined_radius - distance) / device_accuracy
        scam_score = int(20 + (1 - match_percentage) * 30)  # 20-50 range
    elif distance <= radius * 2:
        # Near miss - higher scam probability
        verification_result = "NEAR_MISS"
        distance_factor = (distance - combined_radius) / radius
        scam_score = int(50 + distance_factor * 25)  # 50-75 range
    else:
        # Far away - very high scam probability
        verification_result = "NO_MATCH"
        # Scale based on how far away (max at 10x radius)
        max_distance = radius * 10
        distance_factor = min(distance / max_distance, 1.0)
        scam_score = int(75 + distance_factor * 24)  # 75-99 range
    
    result = {
        "scamScore": max(1, min(100, scam_score)),
        "verificationResult": verification_result,
        "lastLocationTime": last_location_time,
        "phone_number": phone_number,
        "status": "success",
        "distance_meters": round(distance, 2),
        "expected_radius": radius,
        "device_accuracy": device_accuracy
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
    Verify if a device is within a specified city and return scam score (1-100).
    
    Args:
        phone_number (str): The phone number in E.164 format
        city (str): The name of the city to verify location against
        country (str, optional): The country name
        radius (int): The radius of the area in meters (default: 2000)
        max_age (int, optional): Maximum age of location data in seconds
        
    Returns:
        dict: Contains scam score (1-100) and verification result
    """
    # Load mock data
    mock_data = load_user_data(phone_number)
    
    if not mock_data:
        return {
            "error": f"Phone number {phone_number} not found in mock data",
            "status": "not_found",
            "phone_number": phone_number,
            "scamScore": 95  # High score if user not found
        }
    
    location_data = mock_data.get('data', {}).get('location', {})
    kyc_data = mock_data.get('data', {}).get('kyc', {})
    
    # Simple city match based on KYC locality data
    stored_locality = kyc_data.get('locality', '').lower()
    stored_country = kyc_data.get('country', '').lower()
    
    city_match = city.lower() in stored_locality or stored_locality in city.lower()
    country_match = True if not country else (country.lower() in stored_country or stored_country in country.lower())
    
    # Calculate scam score based on location match
    if city_match and country_match:
        verification_result = "MATCH"
        scam_score = 8  # Very low scam probability for perfect match
    elif city_match:
        verification_result = "CITY_MATCH"
        scam_score = 25  # Low-moderate scam probability for city match only
    elif country_match:
        verification_result = "COUNTRY_MATCH"
        scam_score = 60  # Higher scam probability for country match only
    else:
        verification_result = "NO_MATCH"
        scam_score = 90  # Very high scam probability for no match
    
    result = {
        "scamScore": scam_score,
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

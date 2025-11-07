"""
Mock SIM Swap API - simulates Orange SIM Swap detection
"""
from typing import Optional
from datetime import datetime, timezone
from .data_loader import load_user_data


async def check_sim_swap(phone_number: str, max_age: Optional[int] = None) -> dict:
    """
    Check if a SIM swap has occurred for the given phone number.
    
    Args:
        phone_number (str): The phone number to check.
        max_age (int, optional): Maximum age of SIM swap data in hours. Defaults to 240 (10 days).
    
    Returns:
        dict: Result of the SIM swap check
            - swapped (bool): True if a SIM swap has occurred during the checked period
            - latestSimChange (str): Date of the latest SIM change (if available)
            - phone_number (str): The phone number checked
            - status (str): "success" or "not_found"
    """
    # Load mock data
    mock_data = load_user_data(phone_number)
    
    if not mock_data:
        return {
            "error": f"Phone number {phone_number} not found in mock data",
            "status": "not_found",
            "phone_number": phone_number
        }
    
    sim_swap_data = mock_data.get('data', {}).get('simSwap', {})
    latest_sim_change = sim_swap_data.get('latestSimChange')
    
    if not latest_sim_change:
        return {
            "swapped": False,
            "phone_number": phone_number,
            "status": "success",
            "message": "No SIM swap data available"
        }
    
    # Calculate if swap occurred within max_age hours
    swapped = False
    if max_age is not None:
        try:
            swap_time = datetime.fromisoformat(latest_sim_change.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            hours_since_swap = (current_time - swap_time).total_seconds() / 3600
            swapped = hours_since_swap <= max_age
        except (ValueError, AttributeError):
            swapped = False
    else:
        # If no max_age specified, just return that a swap date exists
        swapped = True
    
    return {
        "swapped": swapped,
        "latestSimChange": latest_sim_change,
        "phone_number": phone_number,
        "status": "success"
    }


async def retrieve_sim_swap_date(phone_number: str) -> dict:
    """
    Retrieve the date of the latest SIM swap for the given phone number.
    
    Args:
        phone_number (str): The phone number to check.

    Returns:
        dict: Result containing the latest SIM swap date
            - latestSimChange (str): Date of the latest SIM swap in ISO 8601 format
            - phone_number (str): The phone number checked
            - status (str): "success" or "not_found"
    """
    # Load mock data
    mock_data = load_user_data(phone_number)
    
    if not mock_data:
        return {
            "error": f"Phone number {phone_number} not found in mock data",
            "status": "not_found",
            "phone_number": phone_number
        }
    
    sim_swap_data = mock_data.get('data', {}).get('simSwap', {})
    latest_sim_change = sim_swap_data.get('latestSimChange')
    
    if not latest_sim_change:
        return {
            "error": "No SIM swap data available for this number",
            "status": "no_data",
            "phone_number": phone_number
        }
    
    return {
        "latestSimChange": latest_sim_change,
        "phone_number": phone_number,
        "status": "success"
    }

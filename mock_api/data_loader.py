"""
Mock data loader utility
Loads and manages mock client data from JSON files
"""
import os
import json
from typing import Optional, Dict, Any

# Path to mock data directory
MOCK_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mock_client_data')


def load_mock_data(phone_number: str) -> Optional[Dict[str, Any]]:
    """
    Load mock data for a specific phone number
    
    Args:
        phone_number (str): Phone number in E.164 format (e.g., "+99012345678")
    
    Returns:
        dict: Mock data for the phone number, or None if not found
    """
    # Iterate through all subdirectories in mock_client_data
    for root, dirs, files in os.walk(MOCK_DATA_DIR):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('phoneNumber') == phone_number:
                            return data
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
    
    return None


def get_all_phone_numbers() -> list:
    """
    Get all available phone numbers from mock data
    
    Returns:
        list: List of all phone numbers in mock data
    """
    phone_numbers = []
    
    for root, dirs, files in os.walk(MOCK_DATA_DIR):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        phone_number = data.get('phoneNumber')
                        if phone_number:
                            phone_numbers.append(phone_number)
                except (json.JSONDecodeError, IOError):
                    continue
    
    return phone_numbers

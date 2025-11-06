"""
Mock API module - simulates Orange API functionality using local mock data
No authentication required - all data served from mock_client_data directory
"""

# SIM Swap Detection
from .sym_swap import check_sim_swap, retrieve_sim_swap_date

# KYC Customer Verification
from .kyc_match import match_customer_data

# Location Verification
from .location_verification import (
    verify_device_location,
    verify_device_location_by_city
)

# Location Retrieval
from .location_retrieval import retrieve_device_location

# Define public API
__all__ = [
    # SIM Swap
    'check_sim_swap',
    'retrieve_sim_swap_date',
    # KYC
    'match_customer_data',
    # Location
    'verify_device_location',
    'verify_device_location_by_city',
    'retrieve_device_location',
]

__version__ = '0.1.0'

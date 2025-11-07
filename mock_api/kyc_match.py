"""
Mock KYC Match API - simulates Orange KYC customer verification
"""
from typing import Optional, Dict, Any
from .data_loader import load_mock_data


async def match_customer_data(
    phone_number: str,
    id_document: Optional[str] = None,
    name: Optional[str] = None,
    given_name: Optional[str] = None,
    family_name: Optional[str] = None,
    name_kana_hankaku: Optional[str] = None,
    name_kana_zenkaku: Optional[str] = None,
    middle_names: Optional[str] = None,
    family_name_at_birth: Optional[str] = None,
    address: Optional[str] = None,
    street_name: Optional[str] = None,
    street_number: Optional[str] = None,
    postal_code: Optional[str] = None,
    region: Optional[str] = None,
    locality: Optional[str] = None,
    country: Optional[str] = None,
    house_number_extension: Optional[str] = None,
    birthdate: Optional[str] = None,
    email: Optional[str] = None,
    gender: Optional[str] = None
) -> Dict[str, Any]:
    """
    Match customer data against mock database
    
    Args:
        phone_number (str): The phone number to verify
        Various optional fields to match against
    
    Returns:
        dict: Match results for each field provided
            - {field}Match (str): "true", "false", or "not_available" for each field
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
    
    kyc_data = mock_data.get('data', {}).get('kyc', {})
    
    # Build result
    result = {
        "phone_number": phone_number,
        "status": "success"
    }
    
    # Check each provided field
    field_mappings = {
        "id_document": ("idDocument", "idDocumentMatch"),
        "name": ("name", "nameMatch"),
        "given_name": ("givenName", "givenNameMatch"),
        "family_name": ("familyName", "familyNameMatch"),
        "name_kana_hankaku": ("nameKanaHankaku", "nameKanaHankakuMatch"),
        "name_kana_zenkaku": ("nameKanaZenkaku", "nameKanaZenkakuMatch"),
        "middle_names": ("middleNames", "middleNamesMatch"),
        "family_name_at_birth": ("familyNameAtBirth", "familyNameAtBirthMatch"),
        "address": ("address", "addressMatch"),
        "street_name": ("streetName", "streetNameMatch"),
        "street_number": ("streetNumber", "streetNumberMatch"),
        "house_number_extension": ("houseNumberExtension", "houseNumberExtensionMatch"),
        "postal_code": ("postalCode", "postalCodeMatch"),
        "region": ("region", "regionMatch"),
        "locality": ("locality", "localityMatch"),
        "country": ("country", "countryMatch"),
        "birthdate": ("birthdate", "birthdateMatch"),
        "email": ("email", "emailMatch"),
        "gender": ("gender", "genderMatch")
    }
    
    for param_name, (kyc_field, result_field) in field_mappings.items():
        param_value = locals()[param_name]
        if param_value is not None:
            kyc_value = kyc_data.get(kyc_field)
            if kyc_value is None:
                result[result_field] = "not_available"
            else:
                # Case-insensitive comparison
                match = str(param_value).lower().strip() == str(kyc_value).lower().strip()
                result[result_field] = "true" if match else "false"
    
    return result

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
    Match customer data against mock database and calculate risk score
    
    Args:
        phone_number (str): The phone number to verify
        Various optional fields to match against
    
    Returns:
        dict: Match results for each field provided
            - {field}Match (str): "true", "false", or "not_available" for each field
            - phone_number (str): The phone number checked
            - status (str): "success" or "not_found"
            - riskScore (int): Risk score from 1-100 (higher = more mismatches = higher scam risk)
            - matchedFields (int): Number of fields that matched
            - mismatchedFields (int): Number of fields that didn't match
            - checkedFields (int): Total number of fields checked
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
    
    # Track statistics for risk calculation
    matched_count = 0
    mismatched_count = 0
    checked_count = 0
    
    for param_name, (kyc_field, result_field) in field_mappings.items():
        param_value = locals()[param_name]
        if param_value is not None:
            checked_count += 1
            kyc_value = kyc_data.get(kyc_field)
            if kyc_value is None:
                result[result_field] = "not_available"
            else:
                # Case-insensitive comparison
                match = str(param_value).lower().strip() == str(kyc_value).lower().strip()
                result[result_field] = "true" if match else "false"
                
                if match:
                    matched_count += 1
                else:
                    mismatched_count += 1
    
    # Calculate risk score (1-100 scale)
    if checked_count == 0:
        risk_score = 50  # No fields checked = medium risk
    else:
        # Calculate mismatch percentage
        mismatch_percentage = (mismatched_count / checked_count) * 100
        
        # Map percentage to 1-100 scale
        # 0% mismatches = 1 (lowest risk)
        # 100% mismatches = 100 (highest risk)
        risk_score = max(1, min(100, int(mismatch_percentage) + 1))
    
    # Add statistics to result
    result["riskScore"] = risk_score
    result["matchedFields"] = matched_count
    result["mismatchedFields"] = mismatched_count
    result["checkedFields"] = checked_count
    
    return result

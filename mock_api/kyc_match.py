"""
Mock KYC Match API - simulates Orange KYC customer verification
"""
from typing import Optional, Dict, Any
from .data_loader import load_user_data


def calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Calculate simple name similarity score (0-1).
    Basic implementation - can be enhanced with fuzzy matching.
    """
    if not name1 or not name2:
        return 0.0
    
    name1_clean = name1.lower().strip()
    name2_clean = name2.lower().strip()
    
    if name1_clean == name2_clean:
        return 1.0
    
    # Check if names contain each other
    if name1_clean in name2_clean or name2_clean in name1_clean:
        return 0.8
    
    # Simple word overlap check
    words1 = set(name1_clean.split())
    words2 = set(name2_clean.split())
    
    if not words1 or not words2:
        return 0.0
    
    overlap = len(words1.intersection(words2))
    total_unique = len(words1.union(words2))
    
    return overlap / total_unique if total_unique > 0 else 0.0


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
    mock_data = load_user_data(phone_number)
    
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
                # Use name similarity for name fields
                if param_name == "name":
                    similarity = calculate_name_similarity(str(param_value), str(kyc_value))
                    # Consider match if similarity >= 0.8
                    match = similarity >= 0.8
                    result[result_field] = "true" if match else "false"
                    result["nameSimilarity"] = round(similarity, 2)
                elif param_name in ["given_name", "family_name"]:
                    similarity = calculate_name_similarity(str(param_value), str(kyc_value))
                    # More lenient for partial names - >= 0.6
                    match = similarity >= 0.6
                    result[result_field] = "true" if match else "false"
                else:
                    # Case-insensitive comparison for other fields
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

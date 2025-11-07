"""
Mock KYC Match API - simulates Orange KYC customer verification
"""
from typing import Optional, Dict, Any
from .data_loader import load_user_data


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


def verify_kyc_data(
    phone_number: str,
    provided_name: Optional[str] = None,
    provided_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Simplified KYC verification for fraud detection.
    Returns a match score instead of individual field matches.
    
    Args:
        phone_number (str): The phone number to verify
        provided_name (str, optional): Name provided by caller
        provided_address (str, optional): Address provided by caller
        
    Returns:
        dict: Verification result with overall match score
            - status (str): "success" or "not_found"
            - overall_match_score (int): 0-100 (higher = better match)
            - phone_number (str): The phone number checked
    """
    # Load mock data
    mock_data = load_user_data(phone_number)
    
    if not mock_data:
        return {
            "error": f"Phone number {phone_number} not found in mock data",
            "status": "not_found",
            "phone_number": phone_number,
            "overall_match_score": 0
        }
    
    kyc_data = mock_data.get('data', {}).get('kyc', {})
    
    scores = []
    
    # Check name match if provided
    if provided_name:
        stored_name = kyc_data.get('name', '')
        stored_given_name = kyc_data.get('givenName', '')
        stored_family_name = kyc_data.get('familyName', '')
        
        if stored_name:
            provided_name_clean = provided_name.lower().strip()
            stored_name_clean = stored_name.lower().strip()
            
            # Check for exact match
            if provided_name_clean == stored_name_clean:
                scores.append(100)
            # Check if provided name contains key parts
            elif stored_given_name.lower() in provided_name_clean and stored_family_name.lower() in provided_name_clean:
                scores.append(90)
            # Check if family name matches at least
            elif stored_family_name.lower() in provided_name_clean:
                scores.append(60)
            # Check if given name matches at least
            elif stored_given_name.lower() in provided_name_clean:
                scores.append(50)
            else:
                scores.append(10)
        else:
            scores.append(50)  # No stored name to compare
    
    # Check address match if provided
    if provided_address:
        stored_address = kyc_data.get('address', '')
        stored_street_name = kyc_data.get('streetName', '')
        
        if stored_address or stored_street_name:
            provided_address_clean = provided_address.lower().strip()
            
            # Check if street name is in provided address
            if stored_street_name and stored_street_name.lower() in provided_address_clean:
                scores.append(90)
            # Check if stored address is in provided address or vice versa
            elif stored_address and (
                provided_address_clean in stored_address.lower() or
                stored_address.lower() in provided_address_clean
            ):
                scores.append(80)
            else:
                scores.append(20)
        else:
            scores.append(50)  # No stored address to compare
    
    # Calculate overall match score
    if scores:
        overall_match_score = int(sum(scores) / len(scores))
    else:
        overall_match_score = 50  # No fields to check
    
    return {
        "status": "success",
        "phone_number": phone_number,
        "overall_match_score": overall_match_score,
        "fields_checked": len(scores)
    }

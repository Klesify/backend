from typing import Optional, Dict, Any
import httpx
from auth import get_access_token


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
    # Get valid OAuth token
    token = await get_access_token()
    
    # API endpoint
    url = "https://api.orange.com/camara/playground/api/kyc-match/v0.2/match"
    
    # Build request payload with only provided parameters
    payload = {"phoneNumber": phone_number}
    
    # Add optional parameters only if provided
    optional_params = {
        "idDocument": id_document,
        "name": name,
        "givenName": given_name,
        "familyName": family_name,
        "nameKanaHankaku": name_kana_hankaku,
        "nameKanaZenkaku": name_kana_zenkaku,
        "middleNames": middle_names,
        "familyNameAtBirth": family_name_at_birth,
        "address": address,
        "streetName": street_name,
        "streetNumber": street_number,
        "postalCode": postal_code,
        "region": region,
        "locality": locality,
        "country": country,
        "houseNumberExtension": house_number_extension,
        "birthdate": birthdate,
        "email": email,
        "gender": gender
    }
    
    # Only include non-None values in payload
    for key, value in optional_params.items():
        if value is not None:
            payload[key] = value
    
    # Headers with Bearer token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Add metadata to result
            result["status"] = "success"
            result["phone_number"] = phone_number
            print(result)
            
            return result
            
    except httpx.HTTPStatusError as e:
        print(f"KYC Match failed with status {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return {
            "error": f"API error: {e.response.status_code}",
            "details": e.response.text,
            "status": "failed",
            "phone_number": phone_number
        }
    except Exception as e:
        print(f"KYC Match failed: {str(e)}")
        return {
            "error": str(e),
            "status": "failed",
            "phone_number": phone_number
        }

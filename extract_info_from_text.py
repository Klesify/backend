"""
Extract User Info - OpenAI-powered extraction of KYC data from natural language text
"""
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()


def extract_user_info(text: str) -> Dict[str, Any]:
    """
    Extract user information from natural language text using OpenAI.
    
    Args:
        text: The natural language text containing user information
        
    Returns:
        dict: Dictionary with extracted KYC fields. Example:
            {
                "name": "Marcel Barosanu",
                "givenName": "Marcel",
                "familyName": "Barosanu",
                "locality": "Sibiu",
                "streetName": "Nicolae Iancu",
                "email": "example@email.com",
                ...
            }
            Returns empty dict {} if extraction fails.
    
    Extractable fields:
        - phoneNumber: Phone number with country code
        - idDocument: ID document number
        - name: Full name
        - givenName: First name
        - middleNames: Middle name(s)
        - familyName: Last name
        - familyNameAtBirth: Maiden name
        - birthdate: Birth date (YYYY-MM-DD format)
        - country: Country (ISO 2-letter code)
        - locality: City
        - region: State/Province
        - address: Full address
        - streetName: Street name
        - streetNumber: House number
        - houseNumberExtension: Apartment/Suite
        - postalCode: Postal code
        - email: Email address
        - gender: Gender (MALE, FEMALE, OTHER)
        - claimsCompanyAffiliation: Boolean - If caller claims to represent a company
        - companyName: Name of the company they claim to represent
    """
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("Error: OpenAI API key not found. Please set OPENAI_API_KEY in .env file")
        return {}
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Build system prompt
        system_prompt = """You are a fraud detection assistant analyzing phone call transcripts. Your task is to extract information about the CALLER (potential scammer) from the conversation.

The caller may be pretending to be someone else or trying to obtain information. Extract ANY identifying information mentioned about the caller, whether they claim it directly or it's implied in the conversation.

Extract these fields about the CALLER if present:
- phoneNumber: Phone number of the caller (format: +country_code and number)
- idDocument: ID document number they mention
- name: Full name the caller claims or uses
- givenName: First name of the caller
- middleNames: Middle name(s)
- familyName: Last name / Surname of the caller
- familyNameAtBirth: Family name at birth (maiden name)
- birthdate: Birth date they mention (format: YYYY-MM-DD)
- country: Country the caller claims to be from or is located in (ISO 2-letter code like RO, US, UK)
- locality: City the caller mentions or is calling from
- region: Region, state, or province
- address: Full address they mention
- streetName: Street name only
- streetNumber: Street number / house number
- houseNumberExtension: Apartment/Suite
- postalCode: Postal code
- email: Email address of the caller
- gender: Gender (MALE, FEMALE, OTHER)
- claimsCompanyAffiliation: Boolean (true/false) - Does the caller claim to represent a company/organization?
- companyName: Name of the company/organization they claim to represent (e.g., "Microsoft", "Bank", "Technical Support")

CRITICAL RULES:
1. Extract information about the CALLER/SCAMMER, not the victim
2. If the caller says "Can you confirm your name is X?", extract X as the name they're trying to verify (potential victim name they know)
3. If the caller says "I'm calling from Y", extract Y as their claimed location
4. Extract ANY information the caller reveals about themselves, even indirectly
5. Look for: claimed company/organization, location mentioned, contact info requested/provided
6. Set claimsCompanyAffiliation to true if caller mentions working for/representing ANY company, organization, bank, support service, government agency, etc.
7. Extract companyName if they mention it (e.g., "Microsoft", "your bank", "technical support", "IRS", "Amazon")
8. Return null for fields not determinable from the conversation
9. Format dates as YYYY-MM-DD
10. Use ISO 2-letter codes for country (RO, US, UK, etc.)
11. Use MALE, FEMALE, or OTHER for gender
12. Use true/false (boolean) for claimsCompanyAffiliation

Return as valid JSON with only the fields above."""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract user information from this text:\n\n{text}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        extracted_data = json.loads(response.choices[0].message.content)
        
        # Remove null values for cleaner output
        extracted_data = {k: v for k, v in extracted_data.items() if v is not None}
        
        return extracted_data
        
    except Exception as e:
        print(f"Error extracting user info: {str(e)}")
        return {}

"""
Fraud Detection System
Processes extracted caller information and returns comprehensive scam score.
"""

import asyncio
from typing import Dict, Any, Optional, List
from mock_api.data_loader import (
    load_user_data, 
    find_employee_by_phone, 
    find_company_by_name,
    load_companies_data
)
from mock_api.location_verification import verify_device_location, verify_device_location_by_city
from mock_api.kyc_match import verify_kyc_data


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


async def detect_fraud(extracted_data: Dict[str, Any], caller_phone: str) -> Dict[str, Any]:
    """
    Comprehensive fraud detection based on extracted caller information.
    
    Args:
        extracted_data (Dict): Data extracted from caller's text using extract_user_info()
        caller_phone (str): The phone number of the caller
        
    Returns:
        Dict: Comprehensive fraud analysis with overall scam score (1-100)
    """
    
    # Initialize result structure
    result = {
        "overall_scam_score": 50,  # Default moderate risk
        "risk_level": "MEDIUM",
        "verification_results": {},
        "risk_factors": [],
        "caller_phone": caller_phone,
        "extracted_data": extracted_data
    }
    
    # Extract caller information
    caller_name = extracted_data.get("name", "")
    caller_location = extracted_data.get("locality", "") or extracted_data.get("location", "")
    caller_country = extracted_data.get("country", "")
    caller_address = extracted_data.get("address", "")
    claimed_company = extracted_data.get("companyName", "") or extracted_data.get("company", "")
    
    # Track individual scores for weighted calculation
    scores = []
    weights = []
    
    # 1. LOCATION VERIFICATION
    location_score = 75  # Default high risk if no location
    
    if caller_location:
        try:
            # Verify location by city
            location_result = await verify_device_location_by_city(
                phone_number=caller_phone,
                city=caller_location,
                country=caller_country
            )
            
            location_score = location_result.get("scamScore", 75)
            result["verification_results"]["location"] = location_result
            
            if location_score > 70:
                result["risk_factors"].append(f"Location mismatch: claimed {caller_location}")
            elif location_score < 30:
                result["risk_factors"].append(f"Location verified: {caller_location}")
                
        except Exception as e:
            result["risk_factors"].append(f"Location verification failed: {str(e)}")
    else:
        result["risk_factors"].append("No location provided")
    
    scores.append(location_score)
    weights.append(0.3)  # 30% weight for location
    
    # 2. COMPANY VERIFICATION (if company claimed)
    company_score = 20  # Default low risk if no company claimed
    
    if claimed_company:
        try:
            # Find company in database
            company_data = find_company_by_name(claimed_company)
            
            if company_data:
                # Check if caller phone matches company phone
                company_phone = company_data.get("company_phone", "")
                
                if caller_phone == company_phone:
                    # Caller is using company's official phone - very suspicious for individual caller
                    company_score = 95
                    result["risk_factors"].append(f"Caller using company's official phone number")
                else:
                    # Check if caller is a legitimate employee
                    employee_data = find_employee_by_phone(caller_phone)
                    
                    if employee_data:
                        # Found employee record - check name match
                        employee_name = employee_data.get("name", "")
                        name_similarity = calculate_name_similarity(caller_name, employee_name)
                        
                        if name_similarity >= 0.8:
                            company_score = 10  # Very low risk - legitimate employee
                            result["risk_factors"].append("Verified employee with name match")
                        elif name_similarity >= 0.5:
                            company_score = 30  # Low-moderate risk - partial name match
                            result["risk_factors"].append("Employee found but name partially matches")
                        else:
                            company_score = 80  # High risk - phone matches but name doesn't
                            result["risk_factors"].append("Employee phone found but name mismatch")
                    else:
                        # Claims company affiliation but not in employee database
                        company_score = 85
                        result["risk_factors"].append(f"Claims {claimed_company} employment but not in employee database")
                        
                result["verification_results"]["company"] = {
                    "company_found": True,
                    "company_data": company_data,
                    "employee_data": employee_data,
                    "name_similarity": calculate_name_similarity(caller_name, employee_data.get("name", "")) if employee_data else 0
                }
            else:
                # Company not found in database
                company_score = 60  # Moderate risk - unknown company
                result["risk_factors"].append(f"Claimed company '{claimed_company}' not found in database")
                result["verification_results"]["company"] = {"company_found": False}
                
        except Exception as e:
            company_score = 70
            result["risk_factors"].append(f"Company verification failed: {str(e)}")
    
    scores.append(company_score)
    weights.append(0.4)  # 40% weight for company verification
    
    # 3. KYC DATA VERIFICATION
    kyc_score = 60  # Default moderate risk
    
    try:
        kyc_result = verify_kyc_data(
            phone_number=caller_phone,
            provided_name=caller_name,
            provided_address=caller_address
        )
        
        if kyc_result.get("status") == "success":
            match_score = kyc_result.get("overall_match_score", 50)
            # Convert match score to scam score (inverse relationship)
            kyc_score = max(1, 100 - match_score)
            
            if match_score >= 80:
                result["risk_factors"].append("Strong KYC data match - low fraud risk")
            elif match_score >= 50:
                result["risk_factors"].append("Partial KYC data match - moderate risk")
            else:
                result["risk_factors"].append("Poor KYC data match - high fraud risk")
        else:
            kyc_score = 80
            result["risk_factors"].append("KYC verification failed or user not found")
            
        result["verification_results"]["kyc"] = kyc_result
        
    except Exception as e:
        kyc_score = 75
        result["risk_factors"].append(f"KYC verification error: {str(e)}")
    
    scores.append(kyc_score)
    weights.append(0.3)  # 30% weight for KYC verification
    
    # 4. CALCULATE WEIGHTED OVERALL SCORE
    if scores and weights:
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        total_weight = sum(weights)
        overall_score = int(weighted_sum / total_weight)
    else:
        overall_score = 75  # High risk if no verification possible
    
    # Ensure score is in valid range
    overall_score = max(1, min(100, overall_score))
    
    # 5. DETERMINE RISK LEVEL
    if overall_score <= 25:
        risk_level = "LOW"
    elif overall_score <= 50:
        risk_level = "MEDIUM"
    elif overall_score <= 75:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    # Update result
    result.update({
        "overall_scam_score": overall_score,
        "risk_level": risk_level,
        "component_scores": {
            "location_score": location_score,
            "company_score": company_score,
            "kyc_score": kyc_score
        },
        "scoring_weights": {
            "location": 0.3,
            "company": 0.4,
            "kyc": 0.3
        }
    })
    
    return result


# Convenience function for quick fraud check
async def quick_fraud_check(extracted_data: Dict[str, Any], caller_phone: str) -> int:
    """
    Quick fraud check that returns only the overall scam score.
    
    Args:
        extracted_data (Dict): Extracted caller information
        caller_phone (str): Caller's phone number
        
    Returns:
        int: Scam score from 1-100 (higher = more likely to be scam)
    """
    result = await detect_fraud(extracted_data, caller_phone)
    return result["overall_scam_score"]


if __name__ == "__main__":
    # Example usage
    sample_extracted_data = {
        "name": "Marcel Barosanu",
        "location": "Sibiu",
        "address": "street Nicolae Iancu",
        "company": "Orange Romania"
    }
    
    async def test():
        result = await detect_fraud(sample_extracted_data, "+40712345678")
        print(f"Fraud Detection Result:")
        print(f"Overall Scam Score: {result['overall_scam_score']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Risk Factors: {result['risk_factors']}")
        
    asyncio.run(test())
import asyncio
from orange_api import *
from mock_api import *
from extract_info_from_text import extract_user_info
from fraud_detector import detect_fraud

# Scammer (Marcel Barosanu) is calling and pretending to be from a bank/company
# We need to extract his real info and verify if he's who he claims to be
CLIENT_CALL_TEXT="""Hello, this is Marcel Barosanu calling from City Bank's fraud prevention department. 
                    I'm calling from our Sibiu office in Romania. 
                    We've detected suspicious activity on your account and I need to verify some information with you. 
                    For security purposes, I can provide you my employee ID if needed. 
                    My direct email is marcelbarosanu@gmail.com if you need to reach me. 
                    Can you please confirm your account details so we can protect your funds?"""

# HIGH SCAM SCORE (>90%) - Scammer pretending to be from a company, using wrong location, wrong name
HIGH_SCAM_CALL_TEXT = """Hi, this is Marcel Popescu from Orange Romania customer service. 
                          I'm calling from our Bucharest headquarters to inform you about a special promotion. 
                          We're offering a discount on your next bill, but I need to verify your account details first. 
                          Can you please provide me with your banking information so we can process the refund?"""

# LOW SCAM SCORE (<10%) - Real Marcel calling with accurate information
LOW_SCAM_CALL_TEXT = """Hello, my name is Marcel Barosanu. I'm calling from Sibiu, Romania. 
                         I live on Strada Vasile Milea, and my email is marcelbarosanu@gmail.com. 
                         I wanted to check on my account status and verify some information about my recent transactions."""

async def test_fraud_detection(call_text: str, phone_number: str, test_name: str):
    """Helper function to test fraud detection on different scenarios"""
    # Extract caller information from call text
    extracted_data = extract_user_info(call_text)
    
    if not extracted_data:
        print(f"{test_name}: No data extracted")
        return
    
    # Run comprehensive fraud detection
    fraud_result = await detect_fraud(extracted_data, phone_number)
    
    print(f"{test_name}: Scam Score = {fraud_result['overall_scam_score']}/100")


async def main():
    try:
        # Test 1: Original medium-high risk scenario
        await test_fraud_detection(
            CLIENT_CALL_TEXT, 
            "+99012345678",
            "MEDIUM SCAM - Fake company affiliation"
        )
        
        # Test 2: High scam score scenario (>90%)
        await test_fraud_detection(
            HIGH_SCAM_CALL_TEXT,
            "+40799999999",
            "HIGH SCAM - Fake name, company, location"
        )
        
        # Test 3: Low scam score scenario (<10%)
        await test_fraud_detection(
            LOW_SCAM_CALL_TEXT,
            "+99012345678",
            "LOW SCAM - Legitimate user with accurate info"
        )

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    


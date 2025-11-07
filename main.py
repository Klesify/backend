import asyncio
from orange_api import *
from extract_info_from_text import extract_user_info

# Scammer (Marcel Barosanu) is calling and pretending to be from a bank/company
# We need to extract his real info and verify if he's who he claims to be
CLIENT_CALL_TEXT="""Hello, this is Marcel Barosanu calling from City Bank's fraud prevention department. 
                    I'm calling from our Sibiu office in Romania. 
                    We've detected suspicious activity on your account and I need to verify some information with you. 
                    For security purposes, I can provide you my employee ID if needed. 
                    My direct email is marcelbarosanu@gmail.com if you need to reach me. 
                    Can you please confirm your account details so we can protect your funds?"""

async def main():
    try:
        extracted_data = extract_user_info(CLIENT_CALL_TEXT)
        
        if extracted_data:
            print("Extracted:", ", ".join([f"{k}={v}" for k, v in extracted_data.items()]))
        else:
            print("No data extracted (check if OpenAI API key is set in .env)")
        
        phone_number = "+99012345678"

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    


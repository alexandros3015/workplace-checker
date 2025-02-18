import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

company = input("Enter Company name: ")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash', generation_config={
    "response_mime_type":"application/json",
    "temperature": 0
})

response = model.generate_content(
    f"""
    Given an input company name, return its canonical corporate entity name (using the parent company name if it represents a division—e.g., "Amazon Arizona help desk" becomes "Amazon"—but if it's a standalone company like "McDonalds paint supply", return it as provided) and a boolean flag that is true if the input exactly matches a verified corporate entity (e.g., "McDonalds" returns true) and false if it does not (e.g., "driver" returns false).

    Ensure you fix any spelling errors
    The name of the company/job goes into name, and the verification status goes into needVerify

    Return like:

        \"companies\": [name: string, needVerify: boolean] 
        

    Your provided compnay name is: {company}

    """
)

print(response.text)
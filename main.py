import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from googlesearch import search

load_dotenv() # Gets API key from .env file

company = input("Enter Company name: ")

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) # Configures the API key

model = genai.GenerativeModel('gemini-1.5-flash', generation_config={
    "response_mime_type":"application/json", # Ensure the response is in JSON format
    "temperature": 0 # Makes the response return the same thing every time given the same input
})

ammount_check = model.generate_content(
    f"You are given a selection of companies, tell me how many there are. Return as a JSON object with the following keys: {{'count', int., 'names': [string]}} Company Selection: {company}"  
)

ammount_check = json.loads(ammount_check.text)

print(ammount_check)

company_search = [] # Searches for company on Google. Returns first 2 results
for i in ammount_check["names"]:
    company_search.append(list(search(i, tld="com", num=2, stop=2, pause=2)))

# prompt
response = model.generate_content(
    f"""
        Process the input company name to return a canonical corporate entity name and a verification status. 

        Here is some search results for the input company name:
        {company_search}
        If any of the search results line up with the given company name, it is likely a valid corporate entity and needVerify is True.
        Do keep in mind that the input name may not be a valid corporate entity, and search results may return things related to the subject of a job where needVerify is false

        ### Rules:
        1. **Correct any spelling errors** in the input name.
        2. If the corrected name represents a **division or subsidiary** of a known parent company 
        (e.g., 'Amazon Arizona help desk' → 'Amazon'), return the parent company name.
        3. If it is a **standalone company**, return the corrected name as-is.
        4. **Set 'needVerify' to true if the corrected or parent company name exists as a known, verified corporate entity.**
        - If the name is not a verified corporate entity, set `'needVerify'` to `false`.
        - **Even if the input contains a department (e.g., "Amazon HR"), but it maps to a verified company (Amazon), set `needVerify` to true.**
        5. For ambiguous cases where **multiple parent companies** could apply (e.g., 'Delta Services'), 
        list all valid parents.

        ### Examples:
        - **Input:** 'Amazoon IT'  
        **Output:** {{ "companies": [{{ "name": "Amazon", "needVerify": true }}] }}  

        - **Input:** 'Starbucks'  
        **Output:** {{ "companies": [{{ "name": "Starbucks", "needVerify": true }}] }}  

        - **Input:** 'McDonalds paint supply'  
        **Output:** {{ "companies": [{{ "name": "McDonalds Paint Supply", "needVerify": true }}] }}  

        - **Input:** 'Amazon HR'  
        **Output:** {{ "companies": [{{ "name": "Amazon", "needVerify": true }}] }}  

        - **Input:** 'Self'  
        **Output:** {{ "companies": [{{ "name": "Self", "needVerify": false }}] }}  

        - **Input:** 'Delta Services'  
        **Output:** {{ "companies": [{{ "name": "Delta Airlines", "needVerify": true }}, 
                                    {{ "name": "Delta Faucets", "needVerify": true }}] }}  

        Respond only with the JSON object, no extra text.

        ### Return format:
        ```json
        {{
            "companies": [
                {{
                    "name": "string",
                    "needVerify": boolean
                }}
            ]
        }}

    Your provided compnay name is: {company}

    """
)

print(response.text)


# Parse the response
data = json.loads(response.text)

companies = data.get("companies", [])

# Loop through the companies and check if needVerify is True
for item in companies:
    company_name = item.get("name")

    if item.get("needVerify") == True:
        print("Searching for company on Google")

        # Search for the company on Google
        search_results = list(search(company_name, tld="com", num=10, stop=10, pause=2))
        print(search_results)

        os.remove(".google-cookie") # Remove the cookie file

        link_response = model.generate_content(
            f'''
                Earlier, you were asked to verify a company name.
                That company name is: {company_name}

                I searched for the company on Google and found the following results:
                {search_results}

                Please provide your perdicted name of the company website.

                Return as 

                ```json
                    {{
                        "url": string or null
                        "isVerified": boolean
                        "listIndex": integer or null
                    }}
                ```

                '''
            )
        
        # Parse the response
        final_data = json.loads(link_response.text)
        print(f"\nComapny: {company_name}. Verification status: {final_data['isVerified']}. Url: {final_data['url']}") 

    else:
        print(f"\nComapny: {company_name}. Verification deemed N/A.")



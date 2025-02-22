import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from googlesearch import search

load_dotenv()

company = input("Enter Company name: ")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash', generation_config={
    "response_mime_type":"application/json",
    "temperature": 0
})

response = model.generate_content(
    f"""
        Process the input company name to return a canonical corporate entity name and a verification status. 

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

data = json.loads(response.text)

companies = data.get("companies", [])


for item in companies:

    if item.get("needVerify") == True:
        print("Searching for company on Google")

        search_results = list(search(company, tld="com", num=10, stop=10, pause=2))
        print(search_results)

        os.remove(".google-cookie")

        link_response = model.generate_content(
            f'''
                Earlier, you were asked to verify a company name.
                That company name is: {company}

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
        print(link_response.text)
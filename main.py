import google.generativeai as genai
import os

genai.configure(api_key="Delevopment")

model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("The opposite of cold is: RETURN A JSON RESPONSE")
print(response.text)
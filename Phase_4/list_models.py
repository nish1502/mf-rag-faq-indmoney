import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Listing models with embedding support:")
for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(f"Name: {m.name}, Display: {m.display_name}")

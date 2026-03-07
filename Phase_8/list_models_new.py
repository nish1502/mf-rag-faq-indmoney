import os
from google import genai
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Listing models available via google-genai SDK:")
try:
    for model in client.models.list():
        # Print the whole object to see available attributes
        print(model)
except Exception as e:
    print(f"Error listing models: {e}")

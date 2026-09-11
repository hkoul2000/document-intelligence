import os

from dotenv import load_dotenv
from google import genai


# Load variables from .env
load_dotenv()

# Get the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=api_key)

# Send a simple test request
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello and confirm that you are working."
)

print("\n========== GEMINI RESPONSE ==========\n")
print(response.text)
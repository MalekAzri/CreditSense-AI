import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    response = client.embeddings.create(
        input="Hello world",
        model="text-embedding-3-small"
    )
    print("SUCCESS: API Key is working and has credits.")
except Exception as e:
    print(f"FAILED: {e}")

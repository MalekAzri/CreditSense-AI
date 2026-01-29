import os
import json
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_EMAILS_URL")
QDRANT_API_KEY = os.getenv("QDRANT_EMAILS_API_KEY")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

try:
    res = client.scroll(collection_name="synthetic_emails", limit=10)
    for point in res[0]:
        print(f"ID: {point.id}")
        print(f"Intent: {point.payload.get('intent')}")
        print(f"Tone: {point.payload.get('tone')}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

URL = os.getenv("QDRANT_EMAILS_URL")
KEY = os.getenv("QDRANT_EMAILS_API_KEY")

print(f"Testing connection to: {URL}")
try:
    client = QdrantClient(url=URL, api_key=KEY)
    version = client.get_collections()
    print("✅ Success! Collections found.")
except Exception as e:
    print(f"❌ Failed: {e}")

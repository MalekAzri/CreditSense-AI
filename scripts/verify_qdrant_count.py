import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

try:
    collection_info = client.get_collection("synthetic_emails")
    print(f"Points count: {collection_info.points_count}")
    print(f"Status: {collection_info.status}")
    
    # Check a few points
    res = client.scroll(collection_name="synthetic_emails", limit=1)
    if res[0]:
        print("Success: Found point in Qdrant")
        print("Sample Payload:", res[0][0].payload.get("intent"))
    else:
        print("Warning: Collection is empty")
except Exception as e:
    print(f"FAILED to verify: {e}")

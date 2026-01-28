import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not QDRANT_URL or not QDRANT_API_KEY:
    print("❌ Qdrant credentials missing.")
    exit()

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

try:
    cols = client.get_collections()
    print("Collections:", [c.name for c in cols.collections])
    
    if "synthetic_emails" in [c.name for c in cols.collections]:
        count = client.count(collection_name="synthetic_emails").count
        print(f"Count in 'synthetic_emails': {count}")
        
        # Peek at one item
        points, _ = client.scroll(collection_name="synthetic_emails", limit=1, with_payload=True)
        if points:
            print("Sample payload:", points[0].payload)
    else:
        print("❌ 'synthetic_emails' collection NOT found.")

except Exception as e:
    print(f"Error: {e}")

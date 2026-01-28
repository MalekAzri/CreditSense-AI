import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from project root
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

# Configuration from .env
QDRANT_USE_CLOUD = os.getenv("QDRANT_USE_CLOUD", "False").lower() == "true"
QDRANT_CLOUD_URL = os.getenv("QDRANT_CLOUD_URL", "")
QDRANT_CLOUD_API_KEY = os.getenv("QDRANT_CLOUD_API_KEY", "")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

if QDRANT_USE_CLOUD:
    BASE_URL = QDRANT_CLOUD_URL
    HEADERS = {
        "Content-Type": "application/json",
        "api-key": QDRANT_CLOUD_API_KEY
    }
else:
    BASE_URL = f"http://{QDRANT_HOST}:{QDRANT_PORT}"
    HEADERS = {"Content-Type": "application/json"}

def check_collection(name):
    url = f"{BASE_URL}/collections/{name}"
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            count = data.get("result", {}).get("points_count", 0)
            print(f"✓ Collection '{name}': {count} points")
        elif r.status_code == 404:
            print(f"✗ Collection '{name}': Not found (empty)")
        else:
            print(f"✗ Collection '{name}': Error {r.status_code} - {r.text}")
    except Exception as e:
        print(f"✗ Collection '{name}': Connection failed - {e}")

if __name__ == "__main__":
    mode = "Qdrant Cloud" if QDRANT_USE_CLOUD else "Local Qdrant"
    print(f"Checking {mode} at {BASE_URL}...\n")
    
    collections = [
        "cin_clip_vectors", "cin_ocr_vectors",
        "passport_clip_vectors", "passport_ocr_vectors",
        "bts_loan_app_clip_vectors", "bts_loan_app_ocr_vectors"
    ]
    
    for c in collections:
        check_collection(c)

import sys
import os

# Add the project root to sys.path to find module-verification-docs
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
module_path = os.path.join(project_root, "module-verification-docs")

if module_path not in sys.path:
    sys.path.append(module_path)

import json
from dotenv import load_dotenv

# Load .env explicitly
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

# Debug: Print environment variables
print(f"DEBUG: QDRANT_USE_CLOUD = {os.getenv('QDRANT_USE_CLOUD')}")
print(f"DEBUG: QDRANT_CLOUD_URL = {os.getenv('QDRANT_CLOUD_URL')}")
print(f"DEBUG: Has API Key = {bool(os.getenv('QDRANT_CLOUD_API_KEY'))}")

from verification import verify_document

if __name__ == "__main__":
    test_image = r"d:\CreditSense Ai\module-verification-docs\docs\22_CIN_CIN.png"
    
    print(f"\nTesting verification for: {test_image}")
    result = verify_document(test_image, "CIN")
    
    print(f"\n{'='*60}")
    print("VERIFICATION RESULT:")
    print(f"{'='*60}")
    print(json.dumps({
        "is_valid": result["is_valid"],
        "clip_similarity": result["clip_similarity"],
        "ocr_similarity": result["ocr_similarity"],
        "clip_threshold": result["clip_threshold"],
        "ocr_threshold": result["ocr_threshold"],
        "errors": result["errors"]
    }, indent=2))

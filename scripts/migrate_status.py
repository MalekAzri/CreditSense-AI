from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "credit_platform")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Update all "processed_phase2" to "processed"
result = db.messages.update_many(
    {"status": "processed_phase2"},
    {"$set": {"status": "processed"}}
)

print(f"Updated {result.modified_count} documents from 'processed_phase2' to 'processed'.")

# Verify one document
doc = db.messages.find_one({"status": "processed"})
if doc:
    print("\n--- Verified Document ---")
    print(f"ID: {doc['_id']}")
    print(f"Status: {doc['status']}")
    print(f"Source: {doc.get('source')}")
    print(f"Extracted Data: {doc.get('extracted_data')}")
else:
    print("\nNo 'processed' documents found.")

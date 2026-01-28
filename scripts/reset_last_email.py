from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "creditapp")]

# Trouver le dernier email traité
latest = db.messages.find_one({"status": "processed"}, sort=[("processed_at", -1)])

if latest:
    print(f"Resetting email: {latest.get('subject')} (ID: {latest['_id']})")
    db.messages.update_one(
        {"_id": latest["_id"]},
        {"$set": {"status": "raw", "extracted_data": None, "vectorized": False}}
    )
    print("✅ Reset to raw done.")
else:
    print("No processed email found to reset.")

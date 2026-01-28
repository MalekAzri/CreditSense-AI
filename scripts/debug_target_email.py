from pymongo import MongoClient
import os
import re
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "creditapp")]

# Try to find by Subject regex
target = db.messages.find_one({"subject": {"$regex": "Besoin info", "$options": "i"}})

if not target:
    print("Could not find 'Besoin info' by subject. Trying last non-google...")
    target = db.messages.find_one(
        {'sender': {'$not': {'$regex': 'google', '$options': 'i'}}},
        sort=[('_id', -1)]
    )

if target:
    print(f"FOUND ID: {target.get('_id')}")
    print(f"SUBJECT: {target.get('subject')}")
    print(f"SENDER: {target.get('sender')}")
    print("-" * 20)
    print("CONTENT:")
    print(target.get('clean_text', 'NO CLEAN TEXT'))
else:
    print("NO EMAIL FOUND MATCHING CRITERIA")

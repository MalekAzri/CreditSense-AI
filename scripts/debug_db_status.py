from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "credit_platform")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print(f"Connected to DB: {DB_NAME}")
count = db.messages.count_documents({})
print(f"Total documents: {count}")

pipeline = [
    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
]
results = db.messages.aggregate(pipeline)

print("\nStatus counts:")
for res in results:
    print(f"Status: '{res['_id']}' -> Count: {res['count']}")

# Print one doc just in case
one_doc = db.messages.find_one()
if one_doc:
    print("\nSample Document Keys:", one_doc.keys())
    print("Sample Status:", one_doc.get('status'))

from pymongo import MongoClient
import os
import pprint
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['creditapp']

# Check for successful analysis
count = db.messages.count_documents({"similarity_results": {"$exists": True}})
print(f"Emails with similarity results: {count}")

# Show one
doc = db.messages.find_one({"similarity_results": {"$exists": True}})
if doc:
    print("--- Sample Analysis ---")
    pprint.pprint(doc['similarity_results'])
    print("Subject:", doc.get('subject'))

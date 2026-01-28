from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client['creditapp']

# Check last 5 messages
print("--- LAST 5 MESSAGES ---")
messages = list(db.messages.find(sort=[("_id", -1)]).limit(5))
for m in messages:
    print(f"ID: {m['_id']} | Subject: {m.get('subject')} | Date: {m.get('timestamp')}")
    print(f"  Clean Text: {m.get('clean_text', '')[:100]}...")
    print(f"  Extracted: {m.get('extracted_data')}")
    print(f"  Similarity: {m.get('similarity_results', {}).get('top_intent')}")
    print("-" * 20)

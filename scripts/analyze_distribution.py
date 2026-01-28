from pymongo import MongoClient
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['creditapp']

# Fetch all with results
docs = list(db.messages.find({"similarity_results": {"$exists": True}}))
total = len(docs)

intents = [d.get('similarity_results', {}).get('top_intent', 'UNKNOWN') for d in docs]
counts = Counter(intents)


with open("distribution.txt", "w", encoding="utf-8") as f:
    f.write(f"--- SIMILARITY DISTRIBUTION (Total: {total}) ---\n\n")
    for intent, count in counts.items():
        f.write(f"📊 {intent}: {count} emails ({count/total:.1%})\n")
        examples = [d['subject'] for d in docs if d.get('similarity_results', {}).get('top_intent') == intent][:3]
        for ex in examples:
            f.write(f"   - {ex}\n")
        f.write("\n")
print("Written to distribution.txt")

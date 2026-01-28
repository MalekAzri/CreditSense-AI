from pymongo import MongoClient
import os
import pprint
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['creditapp']

# Fetch 3 emails with similarity results, ideally different ones
docs = db.messages.find({"similarity_results": {"$exists": True}}).limit(3)


with open("examples.txt", "w", encoding="utf-8") as f:
    f.write("--- EXAMPLES OF AI UNDERSTANDING ---\n\n")
    for doc in docs:
        f.write(f"📧 Email Subject: {doc.get('subject')}\n")
        f.write(f"📝 Content Preview: {doc.get('clean_text', '')[:100]}...\n")
        
        sim = doc.get('similarity_results', {})
        f.write(f"🤖 AI Analysis:\n")
        f.write(f"   • Detected Intent: {sim.get('top_intent')} (Confidence: {sim.get('confidence')})\n")
        f.write(f"   • Detected Tone: {sim.get('tone_estimation')}\n")
        f.write(f"   • Similar to Reference IDs: {sim.get('matched_examples')}\n")
        f.write("-" * 50 + "\n\n")
print("Written to examples.txt")

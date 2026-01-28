import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.services.email_processor import EmailProcessor
from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client['creditapp']
processor = EmailProcessor()

# Create dummy message
msg = {
    "source": "debug",
    "sender": "debug@gmail.com",
    "timestamp": datetime.now().isoformat(),
    "content_text": "Je veux un crédit auto de 50000 EUR",
    "subject": "Debug Credit Request",
    "status": "raw"
}

res = db.messages.insert_one(msg)
msg_id = str(res.inserted_id)
print(f"Created message {msg_id}")

# Run Sync
print("Running processor...")
try:
    result = processor.process_single_email(msg_id)
    with open("result_only.txt", "w", encoding="utf-8") as f:
        import json
        # remove datetime for json dump
        if "processed_at" in result: del result["processed_at"]
        f.write(str(result))
    print("Result:", result)
except Exception as e:

    print("Error:", e)
    import traceback
    traceback.print_exc()

# Check DB
doc = db.messages.find_one({"_id": res.inserted_id})
print("Similarity in DB:", doc.get('similarity_results'))

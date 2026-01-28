import requests
from datetime import datetime
import time
from pymongo import MongoClient
import os
import pprint
from dotenv import load_dotenv

load_dotenv()
API_URL = "http://localhost:8001/messages/"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['creditapp']

# 1. Send New Email
payload = {
    "source": "gmail",
    "sender": "new.client@gmail.com", # NOT user email, so it should be processed
    "timestamp": datetime.now().isoformat(),
    "content_text": "Bonjour, je voudrais un crédit auto de 40000 DT sur 4 ans pour acheter une Golf. Merci.",
    "subject": "Demande de prêt auto",
    "status": "raw"
}

print(f"[TEST] Sending test email: {payload['subject']}...")
try:
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    msg_id = data['id']
    print(f"[OK] Response: {data}")
except Exception as e:
    print(f"[ERROR] Failed to reach API: {e}")
    exit()

# 2. Monitor MongoDB for Updates
print(f"⏳ Waiting for processing (ID: {msg_id})...")
for i in range(10): # Wait up to 20s
    time.sleep(2)
    doc = db.messages.find_one({"_id": requests.structures.CaseInsensitiveDict(response.headers) if False else None}) # Id logic is tricky with ObjectIds vs Str
    # We need to query by ObjectId
    from bson import ObjectId
    doc = db.messages.find_one({"_id": ObjectId(msg_id)})
    
    if doc:
        status = doc.get("status")
        vectorized = doc.get("vectorized")
        sim_results = doc.get("similarity_results")
        
        print(f"   [{i*2}s] Status: {status} | Vectorized: {vectorized} | Similarity: {'DONE' if sim_results else 'PENDING'}")
        
        if sim_results:
            print("\n[SUCCESS] PROCESSING COMPLETE!")
            print("--- Analysis Result ---")
            pprint.pprint(sim_results)
            break
else:
    print("[TIMEOUT] Timeout waiting for processing.")

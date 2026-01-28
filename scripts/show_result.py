from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pprint

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client['creditapp']

doc = db.messages.find_one(sort=[("_id", -1)])

print("="*50)
print("TEST RESULT (REAL-TIME)")
print("="*50)
print(f"Subject   : {doc.get('subject')}")
print(f"Sender    : {doc.get('sender')}")
print(f"Status    : {doc.get('status')}")

ext = doc.get("extracted_data", {})
if ext:
    print("\nEXTRACTED DATA (PHASE 1 & 2):")
    print(f"  Clean Text: {doc.get('clean_text')[:100]}...")
    print(f"  Credit Type: {ext.get('credit_type')}")
    print(f"  Amount: {ext.get('amount')} {ext.get('currency')}")
    client = ext.get("client_info", {})
    print(f"  Client Name: {client.get('name')}")
    print(f"  Phone: {client.get('phone')}")
    print(f"  CIN: {client.get('cin')}")
    print(f"  Reference: {ext.get('reference')}")

sim = doc.get("similarity_results", {})
if sim:
    print("\nAI ANALYSIS:")
    print(f"  Intent     : {sim.get('top_intent')}")
    print(f"  Confidence : {sim.get('confidence')}")
    
    tone = sim.get("tone_estimation", {})
    if tone:
        print(f"  Tone       : Urgency={tone.get('urgency')}, Stress={tone.get('stress')}, Seriousness={tone.get('seriousness')}")
else:
    print("\n[WARNING] No similarity result found.")

print("="*50)

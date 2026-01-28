from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client['creditapp']

doc = db.messages.find_one(sort=[("_id", -1)])

print("="*50)
print("FINAL TEST RESULT (LATEST EMAIL)")
print("="*50)
print(f"Subject   : {doc.get('subject')}")
print(f"Sender    : {doc.get('sender')}")
print(f"Status    : {doc.get('status')}")

print("\nPHASE 1 & 2 (EXTRACTION):")
print(f"Clean Text: {doc.get('clean_text')}")
ext = doc.get("extracted_data", {})
if ext:
    print(f"  Credit Type: {ext.get('credit_type')}")
    print(f"  Amount     : {ext.get('amount')} {ext.get('currency')}")
    client_info = ext.get("client_info", {})
    if client_info:
        print(f"  Client Name: {client_info.get('name')}")
        print(f"  Phone      : {client_info.get('phone')}")
        print(f"  CIN        : {client_info.get('cin')}")
    print(f"  Reference  : {ext.get('reference')}")
else:
    print("  (No extracted data found)")

sim = doc.get("similarity_results", {})
if sim:
    print("\nPHASE 4 & 5 (AI ANALYSIS):")
    print(f"  Intent     : {sim.get('top_intent')}")
    print(f"  Confidence : {sim.get('confidence')}")
    print(f"  Tone       : {sim.get('tone_estimation')}")
else:
    print("\n(No AI analysis found)")

print("="*50)

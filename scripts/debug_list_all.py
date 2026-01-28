from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "creditapp")]

print(f"Connected to DB: {db.name}")
print(f"Collection: messages")
count = db.messages.count_documents({})
print(f"Total documents: {count}")

for e in db.messages.find():
    print(f"ID: {e.get('_id')} | Sub: {e.get('subject')} | From: {e.get('sender')}")

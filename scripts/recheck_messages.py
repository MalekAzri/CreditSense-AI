from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client['creditapp']

messages = list(db.messages.find(sort=[("_id", -1)]).limit(20))

with open("recent_messages_list.txt", "w", encoding="utf-8") as f:
    f.write(f"Total found: {len(messages)}\n\n")
    for m in messages:
        f.write(f"ID: {m['_id']}\n")
        f.write(f"SENDER: {m.get('sender')}\n")
        f.write(f"SUBJECT: {m.get('subject')}\n")
        text = str(m.get('content_text', m.get('body', '')))
        f.write(f"TEXT PREVIEW: {text[:200]}\n")
        f.write(f"EXTRACTED DATA: {m.get('extracted_data')}\n")
        f.write("-" * 20 + "\n")

print(f"Logged {len(messages)} messages to recent_messages_list.txt")

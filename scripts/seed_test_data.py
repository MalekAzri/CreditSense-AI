from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "credit_platform")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Clear existing to be clean? No, just add.
# db.messages.delete_many({})

raw_message = {
    "source": "email",
    "sender": "client@example.com",
    "subject": "Demande de crédit pro",
    "content_text": "Bonjour, je souhaite demander un credit professionnel de 50000 DT pour mon entreprise. Mon CA est bon.",
    "timestamp": datetime.now().isoformat(),
    "attachments": [],
    "status": "raw"
}

result = db.messages.insert_one(raw_message)
print(f"Inserted raw message with ID: {result.inserted_id}")

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "creditapp")]

# Reset all non-google emails from last hour to raw
result = db.messages.update_many(
    {
        "sender": {"$not": {"$regex": "google", "$options": "i"}},
        "status": "processed"
    },
    {"$set": {"status": "raw", "extracted_data": None}}
)
print(f"Reset {result.modified_count} emails to raw.")

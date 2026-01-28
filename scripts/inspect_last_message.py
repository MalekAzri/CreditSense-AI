from pymongo import MongoClient
import os
import pprint
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['creditapp']

doc = db.messages.find_one(sort=[("_id", -1)])
print("ID:", doc.get('_id'))
print("Sender:", doc.get('sender'))
print("Subject:", doc.get('subject'))
print("Status:", doc.get('status'))
print("Vectorized Status:", doc.get('vectorization_status'))
print("Similarity Result:", doc.get('similarity_results'))

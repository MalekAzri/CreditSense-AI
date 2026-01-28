from pymongo import MongoClient
import os
import pprint
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['creditapp']

print("Total emails:", db.messages.count_documents({}))

q_processed = {"status": "processed"}
print("Processed:", db.messages.count_documents(q_processed))

q_vectorized = {"status": "processed", "vectorized": True}
print("Vectorized:", db.messages.count_documents(q_vectorized))

q_pending = {"status": "processed", "vectorized": True, "similarity_results": {"$exists": False}}
print("Pending Total:", db.messages.count_documents(q_pending))

q_skipped = {"status": "processed", "vectorized": True, "vectorization_status": "skipped_sent"}
print("Skipped Sent:", db.messages.count_documents(q_skipped))

q_received = {"status": "processed", "vectorized": True, "vectorization_status": {"$ne": "skipped_sent"}}
print("Valid Received Total:", db.messages.count_documents(q_received))

q_done = {"status": "processed", "vectorized": True, "vectorization_status": {"$ne": "skipped_sent"}, "similarity_results": {"$exists": True}}
print("Similarity Done:", db.messages.count_documents(q_done))

q_todo = {"status": "processed", "vectorized": True, "vectorization_status": {"$ne": "skipped_sent"}, "similarity_results": {"$exists": False}}
print("Similarity Pending:", db.messages.count_documents(q_todo))



print(f"Using DB: {db.name}")
print(f"Env DB_NAME: {os.getenv('DB_NAME')}")


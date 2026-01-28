import os
import sys
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "credit_platform")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = "email_vectors"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
USER_EMAIL = os.getenv("USER_EMAIL", "youssefturki999@gmail.com") # Default to observed email if not set

def get_mongo_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def get_qdrant_client():
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in .env")
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def is_received_email(sender: str) -> bool:
    """
    Determines if an email was received based on the sender.
    If the sender contains the user's email, it's considered 'sent' by the user.
    """
    if not sender:
        return False
    # Simple check: is USER_EMAIL in sender string?
    # e.g. "Youssef Turki <youssefturki999@gmail.com>" -> contains "youssefturki999@gmail.com"
    return USER_EMAIL.lower() not in sender.lower()

def main():
    logging.info("🚀 Starting Email Vectorization (Module 4)...")

    # 1. Connect to Services
    try:
        db = get_mongo_db()
        qdrant = get_qdrant_client()
        logging.info("✅ Connected to MongoDB and Qdrant.")
    except Exception as e:
        logging.error(f"❌ Connection failed: {e}")
        return

    # 2. Load Model
    logging.info(f"📥 Loading model '{MODEL_NAME}'... (this may take a moment)")
    try:
        model = SentenceTransformer(MODEL_NAME)
        embedding_dim = model.get_sentence_embedding_dimension() # Should be 384
        logging.info(f"✅ Model loaded. Dimension: {embedding_dim}")
    except Exception as e:
        logging.error(f"❌ Failed to load model: {e}")
        logging.error("Ensure 'sentence-transformers' is installed and C++ Redistributables are present.")
        return

    # 3. Setup Qdrant Collection
    try:
        collections = qdrant.get_collections().collections
        exists = any(c.name == QDRANT_COLLECTION for c in collections)
        
        if not exists:
            logging.info(f"🆕 Creating Qdrant collection '{QDRANT_COLLECTION}'...")
            qdrant.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
            )
        else:
            logging.info(f"ℹ️  Collection '{QDRANT_COLLECTION}' already exists.")
            
    except Exception as e:
        logging.error(f"❌ Qdrant setup failed: {e}")
        return

    # 4. Fetch Emails to Vectorize
    # Filter: status='processed' (so we have clean_text) AND vectorized!=True
    query = {
        "status": "processed",
        "vectorized": {"$ne": True}
    }
    emails_cursor = db.messages.find(query)
    
    emails_to_process = list(emails_cursor)
    logging.info(f"🔍 Found {len(emails_to_process)} processed emails pending vectorization.")
    
    if not emails_to_process:
        logging.info("✅ No new emails to vectorize.")
        return

    points = []
    updated_ids = []

    for email in emails_to_process:
        try:
            email_id = email.get("_id")
            sender = email.get("sender", "")
            subject = email.get("subject", "")
            clean_text = email.get("clean_text", "")
            
            # 5. Check Direction (Received vs Sent)
            if not is_received_email(sender):
                logging.info(f"⏩ Skipping SENT email {email_id} (Subject: {subject})")
                # Mark as 'skipped' or 'vectorized' to avoid reprocessing? 
                # Let's mark as vectorized but with a flag 'skipped_vectorization'
                db.messages.update_one(
                    {"_id": email_id},
                    {"$set": {"vectorized": True, "vectorization_status": "skipped_sent"}}
                )
                continue

            if not clean_text:
                logging.warning(f"⚠️  Email {email_id} has no clean_text. Skipping.")
                continue

            # 6. Generate Embedding
            logging.info(f"🧠 Vectorizing email {email_id}...")
            vector = model.encode(clean_text).tolist()

            # 7. Prepare Qdrant Point
            payload = {
                "mongo_id": str(email_id),
                "subject": subject,
                "sender": sender,
                "clean_text_preview": clean_text[:200], # Store preview
                "timestamp": email.get("timestamp"),
                "direction": "received"
            }
            
            # Use UUID for Qdrant ID, or derive from Mongo ID if possible (Qdrant needs UUID or int)
            point_id = str(uuid.uuid4())
            
            points.append(PointStruct(id=point_id, vector=vector, payload=payload))
            updated_ids.append(email_id)

        except Exception as e:
            logging.error(f"❌ Error processing email {email.get('_id')}: {e}")

    # 8. Upsert to Qdrant
    if points:
        try:
            logging.info(f"b  Upserting {len(points)} vectors to Qdrant...")
            qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
            logging.info("✅ Upsert successful.")
            
            # 9. Update MongoDB
            logging.info("📝 Updating MongoDB status...")
            db.messages.update_many(
                {"_id": {"$in": updated_ids}},
                {"$set": {
                    "vectorized": True,
                    "vectorization_model": MODEL_NAME,
                    "vectorization_date": PointStruct.__module__ # Just a placeholder or current time
                }}
            )
            # Correcting datetime
            from datetime import datetime
            db.messages.update_many(
                {"_id": {"$in": updated_ids}},
                {"$set": {"vectorized_at": datetime.now()}}
            )
            
            logging.info(f"🎉 Successfully vectorized {len(points)} received emails.")
            
        except Exception as e:
            logging.error(f"❌ Failed to upsert/update: {e}")

if __name__ == "__main__":
    main()

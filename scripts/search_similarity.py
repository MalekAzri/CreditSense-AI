import os
import logging
import statistics
from collections import Counter
from dotenv import load_dotenv
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "creditapp") # Ensure we use the correct DB
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = "synthetic_emails" # Reference data
VECTOR_COLLECTION = "email_vectors" # Where our email vectors are stored
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

K_NEIGHBORS = 5

def get_mongo_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def get_qdrant_client():
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in .env")
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def analyze_similarity(target_vector, qdrant_client):
    """
    Search for similar emails in Qdrant and aggregate insights.
    """
    # 1. Search K nearest neighbors
    # Using query_points instead of search (newer API)
    try:
        search_result = qdrant_client.query_points(
            collection_name=QDRANT_COLLECTION,
            query=target_vector,
            limit=K_NEIGHBORS,
            with_payload=True
        ).points
    except AttributeError:
        # Fallback for older clients if query_points exists but returns list directly or something else
        # Or if search DOES exist but failed for other reasons? No, AttributeError was explicit.
        # Let's assume query_points works.
        logging.error("query_points failed or missing.")
        return None
    
    if not search_result:
        return None

    # 2. Extract Data
    intents = []
    tone_scores = {"urgency": [], "stress": [], "seriousness": []}
    matched_ids = []
    
    for point in search_result:
        payload = point.payload
        score = point.score
        matched_ids.append(point.id) # Or payload.get('synthetic_id')
        
        # Intent
        intent = payload.get("intent")
        if intent:
            intents.append(intent)
            
        # Tone
        tone = payload.get("tone", {})
        if tone:
            for k in tone_scores.keys():
                val = tone.get(k)
                if val is not None:
                    tone_scores[k].append(float(val))

    # 3. Aggregate
    
    # Intent Consensus
    if intents:
        # Majority vote
        most_common = Counter(intents).most_common(1)
        top_intent = most_common[0][0]
        confidence = most_common[0][1] / len(intents)
    else:
        top_intent = "UNKNOWN"
        confidence = 0.0
        
    # Tone Average
    avg_tone = {}
    for k, values in tone_scores.items():
        if values:
            avg_tone[k] = round(statistics.mean(values), 2)
        else:
            avg_tone[k] = 0.0

    return {
        "top_intent": top_intent,
        "confidence": round(confidence, 2),
        "tone_estimation": avg_tone,
        "matched_examples": matched_ids,
        "search_score": round(search_result[0].score, 4) # Top score
    }

def main():
    logging.info("🚀 Starting Similarity Search (Module 5)...")
    
    try:
        db = get_mongo_db()
        logging.info(f"Using DB: {db.name}")
        qdrant = get_qdrant_client()
        logging.info("✅ Connected to Services.")
    except Exception as e:
        logging.error(f"❌ Connection failed: {e}")
        return

    # Fetch emails pending analysis
    # Criteria: processed, vectorized, but NO similarity_results
    # Exclude skipped_sent
    query = {
        "status": "processed",
        "vectorized": True,
        "vectorization_status": {"$ne": "skipped_sent"},
        "similarity_results": {"$exists": False}
    }
    
    count_test = db.messages.count_documents(query)
    logging.info(f"Debug: Pending count in DB {db.name} is {count_test}")
    
    # We also need the VECTOR for these emails.
    # Approach 1: Re-embed (slow)
    # Approach 2: Fetch from Qdrant 'email_vectors' by ID (fast)
    
    # Let's try Approach 2. We stored 'mongo_id' in payload, but Qdrant Point ID is separate.
    # But wait, looking at vectorize_emails.py, we generated a random UUID for Qdrant ID.
    # And we updated Mongo with "vectorized": True.
    # We DID NOT store the Qdrant Point ID back in Mongo. (My bad in Module 4 plan, but manageable).
    # However, we stored "mongo_id" in Qdrant Payload.
    # So we can scroll through Qdrant 'email_vectors', get the mongo_id from payload, and update that mongo doc.
    # OR: since we have the model locally, re-embedding clean_text for the few received emails is actually very fast and simpler than reverse lookup.
    
    # Let's go with Re-embedding for simplicity and robustness (ensures vector is fresh).
    # Since we filter for "received" emails only (~24 emails), this is negligible cost.
    
    logging.info("📥 Loading model for vector regeneration...")
    model = SentenceTransformer(MODEL_NAME)
    
    emails_cursor = db.messages.find(query)
    emails = list(emails_cursor)
    
    logging.info(f"🔍 Found {len(emails)} emails pending Similarity Analysis.")
    
    if not emails:
        logging.info("✅ No emails to analyze.")
        return

    count = 0
    for email in emails:
        try:
            email_id = email.get("_id")
            text = email.get("clean_text")
            
            if not text:
                continue
                
            # Vectorize
            vector = model.encode(text).tolist()
            
            # Analyze
            results = analyze_similarity(vector, qdrant)
            
            if results:
                # Update Mongo
                from datetime import datetime
                db.messages.update_one(
                    {"_id": email_id},
                    {"$set": {
                        "similarity_results": results,
                        "analysis_date": datetime.now().isoformat(),
                        "analysis_completed_at": datetime.now()
                    }}
                )
                
                logging.info(f"✅ Analyzed Email {email_id}: Intent={results['top_intent']} (Conf={results['confidence']})")
                count += 1
            else:
                logging.warning(f"⚠️ No neighbors found for {email_id}")
                
        except Exception as e:
            logging.error(f"❌ Error analyzing {email.get('_id')}: {e}")
            
    logging.info(f"🎉 Completed Similarity Search for {count} emails.")

if __name__ == "__main__":
    main()

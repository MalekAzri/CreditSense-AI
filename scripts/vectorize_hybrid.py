import json
import os
import sys
import time
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# Init environment
load_dotenv()

# Configuration
INPUT_FILE = "synthetic_emails.json"
COLLECTION_NAME = "synthetic_emails"

# Qdrant Config
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

class Vectorizer:
    def __init__(self):
        self.mode = None
        self.model_st = None
        self.error = None

        # Priority 1: Sentence Transformers (User's preferred local multilingual model)
        print("[INFO] Loading SentenceTransformers (paraphrase-multilingual-MiniLM-L12-v2)...")
        try:
            from sentence_transformers import SentenceTransformer
            # This requires Visual C++ Redistributable on Windows
            self.model_st = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self.mode = "st"
            print("[SUCCESS] Mode: SentenceTransformers (Local Multilingual) activated.")
        except Exception as e:
            print(f"[ERROR] SentenceTransformers failed: {e}")
            self.error = str(e)
            
            # Fallback to OpenAI only if local fails
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            if OPENAI_API_KEY:
                print("[INFO] Fallback to OpenAI...")
                try:
                    from openai import OpenAI
                    self.client_openai = OpenAI(api_key=OPENAI_API_KEY)
                    self.mode = "openai"
                    print("[SUCCESS] Mode: OpenAI (Cloud) activated.")
                except Exception as e2:
                    print(f"[ERROR] OpenAI fallback failed: {e2}")
                    self.error += f" | OpenAI: {e2}"

    def specific_vectorize(self, text):
        if self.mode == "st":
            return self.model_st.encode(text).tolist()
        elif self.mode == "openai":
            response = self.client_openai.embeddings.create(
                input=text,
                model="text-embedding-3-large"
            )
            return response.data[0].embedding
        else:
            raise RuntimeError(f"No vectorization engine available. Last error: {self.error}")

    def get_dimension(self):
        # paraphrase-multilingual-MiniLM-L12-v2 and all-MiniLM-L6-v2 are 384
        return 384 if self.mode != "openai" else 3072

def main():
    print("[START] starting Vectorization with Multilingual Local Model...")

    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] File '{INPUT_FILE}' not found.")
        return

    if not QDRANT_URL or not QDRANT_API_KEY:
        print("[ERROR] Qdrant Credentials missing in .env")
        return

    try:
        vectorizer = Vectorizer()
        if not vectorizer.mode:
            print("\n[FATAL ERROR] Impossible to vectorize.")
            print("Please ensure sentence-transformers is installed and VC++ Redistributable is active.")
            return
    except Exception as e:
        print(f"[CRITICAL ERROR] Initialization failed: {e}")
        return

    try:
        qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        vector_size = vectorizer.get_dimension()
        
        # We might need to recreate the collection if dimension changed from OpenAI's 3072 to ST's 384
        collections = qdrant.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if exists:
            print(f"[INFO] Collection '{COLLECTION_NAME}' exists. Re-creating for new dimension...")
            qdrant.delete_collection(COLLECTION_NAME)
        
        print(f"[SETUP] Creating collection '{COLLECTION_NAME}' (dim={vector_size})...")
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
    except Exception as e:
        print(f"[ERROR] Qdrant setup failed: {e}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        emails = json.load(f)

    points = []
    print(f"[PROCESSING] Vectorizing {len(emails)} emails...")

    for i, email in enumerate(emails):
        # We combine subject and body for better semantic representation
        text = f"Subject: {email.get('subject', '')}\nContent: {email.get('body', '')}"
        
        try:
            vector = vectorizer.specific_vectorize(text)
            payload = {
                "subject": email.get("subject"),
                "body": email.get("body"),
                "intent": email.get("intent"),
                "tone": email.get("tone"),
                "source": "synthetic",
                "synthetic_id": email.get("synthetic_id")
            }
            points.append(PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload))
        except Exception as e:
            print(f"[WARNING] Skipping email {i} due to error: {e}")

        if (i+1) % 10 == 0:
            print(f"   ... {i+1}/{len(emails)} done.")

    if points:
        print(f"[UPLOAD] Uploading {len(points)} points to Qdrant...")
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
        print("[SUCCESS] All emails have been vectorized and stored in Qdrant Cloud!")
    else:
        print("[WARNING] No points to upload.")

if __name__ == "__main__":
    main()

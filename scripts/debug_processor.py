import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.services.email_processor import EmailProcessor
import logging

logging.basicConfig(level=logging.INFO)

p = EmailProcessor()
text = "Je veux un crédit"
vec = p.embedder.encode(text).tolist()
print(f"Vector dim: {len(vec)}")

res = p._analyze_similarity(vec)
print("Result:", res)

# Check collection info
try:
    info = p.qdrant.get_collection("synthetic_emails")
    print("Collection points:", info.points_count)
except Exception as e:
    print("Collection error:", e)

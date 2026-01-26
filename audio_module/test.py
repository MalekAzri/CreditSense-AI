from app.services.qdrant_service import store_embedding, search_similar

# Embedding fictif (384 dimensions)
fake_embedding = [0.01] * 384

payload = {
    "audio_id": "test_audio_001",
    "user_id": "user_123",
    "confidence_score": 0.82
}

point_id = store_embedding(fake_embedding, payload)
print("✅ Embedding stocké avec ID :", point_id)

results = search_similar(fake_embedding)

print("🔍 Résultats de recherche :")
for r in results:
    print(r)

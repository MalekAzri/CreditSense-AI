"""
Service Qdrant (Cloud) – stockage et recherche vectorielle
"""

import os
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)
from dotenv import load_dotenv
from typing import List, Dict
import uuid

# Charger .env
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "audio_embeddings")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", 384))

if not QDRANT_URL or not QDRANT_API_KEY:
    raise RuntimeError("❌ QDRANT_URL ou QDRANT_API_KEY manquant")

print("🔄 Initialisation de Qdrant Cloud...")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

def init_qdrant():
    """
    Crée la collection si elle n'existe pas
    """
    collections = client.get_collections().collections
    names = [c.name for c in collections]

    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"✅ Collection créée : {COLLECTION_NAME}")
    else:
        print(f"✅ Collection {COLLECTION_NAME} déjà existante")

init_qdrant()
print("✅ Qdrant Cloud prêt")


def store_embedding(
    embedding: List[float],
    payload: Dict
) -> str:
    """
    Stocke un embedding avec metadata
    """
    point_id = str(uuid.uuid4())

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
        ]
    )

    return point_id


def search_similar(
    embedding: List[float],
    limit: int = 5
) -> List[Dict]:
    """
    Recherche vectorielle compatible Qdrant Cloud >= 1.10
    """
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit=limit
    )

    return [
        {
            "id": point.id,
            "score": point.score,
            "payload": point.payload
        }
        for point in response.points
    ]


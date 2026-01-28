"""
Test de connexion à Qdrant Cloud
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

# Connexion à Qdrant Cloud
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Vérification de la connexion
collections = client.get_collections()
print("✅ Connexion à Qdrant Cloud réussie!")
print(f"\nCollections disponibles:")
print(collections)

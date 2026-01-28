from qdrant_client import QdrantClient
import sys

def test_qdrant_connection():
    url = "http://localhost:6333"
    print(f"--- Test de connexion a Qdrant sur {url} ---")
    
    try:
        # Initialiser le client
        client = QdrantClient(url=url)
        
        # 1. Verifier la connexion en listant les collections
        collections_response = client.get_collections()
        collections = collections_response.collections
        
        print("CONNECTE a Qdrant : REUSSIE")
        print(f"Nombre de collections : {len(collections)}")
        
        for col in collections:
            # Recuperer plus d'infos sur la collection
            info = client.get_collection(collection_name=col.name)
            print(f"   - {col.name} ({info.points_count} points)")

        # 2. Lien vers le Dashboard
        print("\nInterface visuelle :")
        print(f"Lien: {url}/dashboard")

    except Exception as e:
        print(f"Erreur de connexion : {e}")
        print("\nConseils :")
        print("1. Verifiez que Docker Desktop est lance.")
        print("2. Lancez Qdrant avec : docker run -p 6333:6333 qdrant/qdrant")

if __name__ == "__main__":
    test_qdrant_connection()

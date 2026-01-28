import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = "email_vectors"

def main():
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("❌ Qdrant credentials missing.")
        return

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    try:
        # Fetch one point
        points, next_page = client.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=1,
            with_payload=True,
            with_vectors=True
        )
        
        if not points:
            print("⚠️ Collection is empty.")
            return

        point = points[0]
        payload = point.payload
        vector = point.vector
        
        with open("vector_output.txt", "w", encoding="utf-8") as f:
            f.write("\n🔍 --- Exemple de Vecteur Reçu ---\n")
            f.write(f"🆔 ID Qdrant: {point.id}\n")
            f.write(f"📧 Sujet: {payload.get('subject')}\n")
            f.write(f"👤 Expéditeur: {payload.get('sender')}\n")
            f.write(f"📄 Extrait Texte Clean: {payload.get('clean_text_preview')}\n")
            f.write(f"↔️ Direction: {payload.get('direction')}\n")
            f.write(f"📏 Dimension du vecteur: {len(vector)}\n")
            f.write(f"🔢 Aperçu du vecteur (5 premières valeurs): {vector[:5]}\n")
            f.write("-----------------------------------\n")
        print("Output written to vector_output.txt")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

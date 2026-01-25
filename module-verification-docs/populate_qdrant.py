"""
Script pour vider et remplir Qdrant avec les vecteurs de référence (Front & Back).
"""

import os
import sys
import uuid
from typing import Dict

# Ajouter le dossier parent au path pour importer verification
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from verification.verify_document import store_reference_vector, get_qdrant_client, ensure_collections_exist
from verification.clip import generate_clip_vector
from verification.ocr import extract_and_embed
from verification.config import get_collection_config

def clear_collection(collection_name: str):
    """Supprime tous les points d'une collection."""
    client = get_qdrant_client()
    if client.collection_exists(collection_name):
        print(f"Suppression des points de la collection: {collection_name}...")
        client.delete(
            collection_name=collection_name,
            points_selector={"has_id": [id for id in client.scroll(collection_name=collection_name, limit=1000)[0]]} if client.scroll(collection_name=collection_name, limit=1)[0] else None,
            # Note: Si la collection est vide, delete avec selector vide peut échouer selon les versions.
            # On utilise une approche plus radicale: recréer la collection ou delete par filtre match_all.
            filter=None # Supprimer tout
        )
        print(f"Collection {collection_name} videe.")

def process_and_store(image_path: str, side: str):
    """Traite une image et stocke ses vecteurs CLIP et OCR."""
    print(f"\nProcessing {side.upper()} side: {image_path}")
    document_type = "CIN"
    
    # 1. CLIP
    print(f"Generating CLIP vector for {side}...")
    clip_vector = generate_clip_vector(image_path)
    if clip_vector is not None:
        point_id = str(uuid.uuid4())
        metadata = {
            "source": f"CIN_{side}_reference",
            "doc_side": side,
            "type": "legitimate"
        }
        store_reference_vector(document_type, "clip", clip_vector, point_id, metadata)
    else:
        print(f"Failed to generate CLIP vector for {side}")

    # 2. OCR
    print(f"Extracting OCR chunks for {side}...")
    text, doc_id, embeddings = extract_and_embed(image_path)
    if embeddings:
        print(f"Storing {len(embeddings)} OCR chunks for {side}...")
        for chunk in embeddings:
            metadata = {
                "source": f"CIN_{side}_reference",
                "doc_side": side,
                "doc_id": doc_id,
                "type": "legitimate",
                "chunk_index": chunk["chunk_index"],
                "text_preview": chunk["text_preview"]
            }
            chunk_point_id = str(uuid.uuid4()) 
            store_reference_vector(document_type, "ocr", chunk["embedding"], chunk_point_id, metadata)
    else:
        print(f"Failed to generate OCR embeddings for {side}")

def main():
    # Chemins des images
    script_dir = os.path.dirname(os.path.abspath(__file__))
    front_path = os.path.join(script_dir, "docs", "CIN.png")
    back_path = os.path.join(script_dir, "docs", "CIN_back.png")
    
    # 1. S'assurer que les collections existent
    ensure_collections_exist("CIN")
    
    # 2. Vider les collections
    config = get_collection_config("CIN")
    client = get_qdrant_client()
    
    client.delete_collection(config["clip_collection"])
    client.delete_collection(config["ocr_collection"])
    
    print("Collections supprimees pour reset complet.")
    ensure_collections_exist("CIN")
    
    # 3. Traiter Front
    if os.path.exists(front_path):
        process_and_store(front_path, "front")
    else:
        print(f"Front image not found: {front_path}")
        
    # 4. Traiter Back
    if os.path.exists(back_path):
        process_and_store(back_path, "back")
    else:
        print(f"Back image not found: {back_path}")

    print("\nQdrant population completed successfully.")

if __name__ == "__main__":
    main()

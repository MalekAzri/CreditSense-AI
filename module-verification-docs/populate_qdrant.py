"""
Script pour vider et remplir Qdrant avec les vecteurs de référence (Front & Back).
"""

import os
import sys
import uuid
from typing import Dict

# Ajouter le dossier parent au path pour importer verification
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from verification import store_reference_vector, ensure_collections_exist, delete_collection
from verification.clip import generate_clip_vector
from verification.ocr import extract_and_embed
from verification.config import get_collection_config

def process_and_store(image_path: str, document_type: str, side: str = "front"):
    """Traite une image et stocke ses vecteurs CLIP et OCR pour un type de doc donné."""
    print(f"\nProcessing {document_type} ({side}): {image_path}")
    
    # 1. CLIP
    print(f"Generating CLIP vector...")
    clip_vector = generate_clip_vector(image_path)
    if clip_vector is not None:
        point_id = str(uuid.uuid4())
        metadata = {
            "source": f"{document_type}_{side}_reference",
            "doc_side": side,
            "type": "legitimate",
            "document_type": document_type
        }
        store_reference_vector(document_type, "clip", clip_vector, point_id, metadata)
    else:
        print(f"Failed to generate CLIP vector for {image_path}")

    # 2. OCR
    print(f"Extracting OCR chunks...")
    text, doc_id, embeddings = extract_and_embed(image_path)
    if embeddings:
        print(f"Storing {len(embeddings)} OCR chunks...")
        for chunk in embeddings:
            metadata = {
                "source": f"{document_type}_{side}_reference",
                "doc_side": side,
                "doc_id": doc_id,
                "type": "legitimate",
                "document_type": document_type,
                "chunk_index": chunk["chunk_index"],
                "text_preview": chunk["text_preview"]
            }
            chunk_point_id = str(uuid.uuid4()) 
            store_reference_vector(document_type, "ocr", chunk["embedding"], chunk_point_id, metadata)
    else:
        print(f"Failed to generate OCR embeddings for {image_path}")

def reset_and_populate(document_type: str, images_map: Dict[str, str]):
    """Reset les collections d'un type de doc et les remplit avec les images fournies."""
    print(f"\n=== Populating {document_type} ===")
    ensure_collections_exist(document_type)
    config = get_collection_config(document_type)
    
    # Reset
    print(f"Resetting collections for {document_type}...")
    delete_collection(config["clip_collection"])
    delete_collection(config["ocr_collection"])
    ensure_collections_exist(document_type)
    
    # Process images
    for side, path in images_map.items():
        if os.path.exists(path):
            process_and_store(path, document_type, side)
        else:
            print(f"Warning: Image not found: {path}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(script_dir, "docs")
    
    # Configuration des documents à peupler
    docs_to_populate = {
        "CIN": {
            "front": os.path.join(docs_dir, "CIN.png"),
            "back": os.path.join(docs_dir, "CIN_back.png")
        },
        "BTS_LOAN_APP": {
            "front": os.path.join(docs_dir, "bts_loan_app.png")
        }
    }
    
    for doc_type, images in docs_to_populate.items():
        reset_and_populate(doc_type, images)

    print("\nQdrant population completed successfully.")

if __name__ == "__main__":
    main()

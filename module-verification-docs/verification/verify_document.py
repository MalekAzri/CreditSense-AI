"""
Vérification de documents via Qdrant HTTP API directement (PUT / POST)
Compatible Qdrant Cloud / local, sans qdrant-client
"""

import sys
import os
import uuid
from typing import Dict, Optional, Union
import requests
from .clip import generate_clip_vector
from .ocr import extract_and_embed
from .config import (
    QDRANT_USE_CLOUD,
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_CLOUD_URL,
    QDRANT_CLOUD_API_KEY,
    get_collection_config,
    get_similarity_thresholds
)

# =========================
# Helper URL et headers
# =========================
def get_qdrant_base_url():
    if QDRANT_USE_CLOUD:
        return QDRANT_CLOUD_URL
    else:
        return f"http://{QDRANT_HOST}:{QDRANT_PORT}"

def get_headers():
    headers = {"Content-Type": "application/json"}
    if QDRANT_USE_CLOUD and QDRANT_CLOUD_API_KEY:
        headers["api-key"] = QDRANT_CLOUD_API_KEY
    return headers

# =========================
# Créer collection si non existante
# =========================
def ensure_collections_exist(document_type: str):
    config = get_collection_config(document_type)
    base_url = get_qdrant_base_url()
    headers = get_headers()

    for coll_name, size in [(config["clip_collection"], config["vector_size_clip"]),
                            (config["ocr_collection"], config["vector_size_ocr"])]:
        url = f"{base_url}/collections/{coll_name}"
        r = requests.get(url, headers=headers)
        if r.status_code == 404:
            # Création
            payload = {
                "vectors": {"size": size, "distance": "Cosine"}
            }
            r_create = requests.put(url, headers=headers, json=payload)
            if r_create.status_code in [200, 201]:
                print(f"Collection créée: {coll_name}")
            else:
                print(f"Erreur création collection {coll_name}: {r_create.text}")

# =========================
# Supprimer collection
# =========================
def delete_collection(collection_name: str):
    base_url = get_qdrant_base_url()
    headers = get_headers()
    url = f"{base_url}/collections/{collection_name}"
    
    r = requests.delete(url, headers=headers)
    if r.status_code == 200:
        print(f"Collection supprimée: {collection_name}")
    elif r.status_code == 404:
        print(f"Collection non existante: {collection_name}")
    else:
        print(f"Erreur suppression collection {collection_name}: {r.text}")

# =========================
# Stocker vecteur
# =========================
def store_reference_vector(
    document_type: str,
    vector_type: str,
    vector,
    point_id: Union[int, str],
    metadata: Optional[Dict] = None
):
    config = get_collection_config(document_type)
    ensure_collections_exist(document_type)

    coll_name = config["clip_collection"] if vector_type == "clip" else config["ocr_collection"]

    base_url = get_qdrant_base_url()
    headers = get_headers()
    url = f"{base_url}/collections/{coll_name}/points"

    payload = {
        "points": [{
            "id": point_id,
            "vector": vector.tolist() if hasattr(vector, "tolist") else vector,
            "payload": metadata or {}
        }]
    }

    r = requests.put(url, headers=headers, json=payload)
    if r.status_code in [200, 201]:
        print(f"Vecteur {vector_type} stocké dans {coll_name} (ID {point_id})")
    else:
        print(f"Erreur stockage vecteur: {r.text}")

# =========================
# Rechercher vecteur
# =========================
def query_qdrant(collection_name: str, vector, limit: int = 1):
    base_url = get_qdrant_base_url()
    headers = get_headers()
    url = f"{base_url}/collections/{collection_name}/points/search"

    payload = {
        "vector": vector.tolist() if hasattr(vector, "tolist") else vector,
        "limit": limit
    }

    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        return r.json().get("result", [])
    else:
        print(f"[ERREUR] Recherche Qdrant: {r.text}")
        return []

# Fuzzy keyword check removed

# =========================
# Vérification document
# =========================
def verify_document(image_path: str, document_type: str = "CIN") -> Dict:
    result = {
        "is_valid": False,
        "clip_similarity": 0.0,
        "ocr_similarity": 0.0,
        "clip_threshold": 0.0,
        "ocr_threshold": 0.0,
        "extracted_text": "",
        "clip_match": None,
        "ocr_match": None,
        "errors": []
    }

    try:
        config = get_collection_config(document_type)
        thresholds = get_similarity_thresholds(document_type)
        result["clip_threshold"] = thresholds["clip_threshold"]
        result["ocr_threshold"] = thresholds["ocr_threshold"]

        ensure_collections_exist(document_type)

        # 1. Vérification CLIP
        print("Génération du vecteur CLIP...")
        print(f"DEBUG: Using collection: {config['clip_collection']}")
        print(f"DEBUG: Qdrant URL: {get_qdrant_base_url()}")
        clip_vector = generate_clip_vector(image_path)
        if clip_vector is not None:
            points = query_qdrant(config["clip_collection"], clip_vector, limit=1)
            print(f"DEBUG: CLIP query returned {len(points)} points")
            if points:
                match = points[0]
                result["clip_similarity"] = match.get("score", 0)
                result["clip_match"] = match
                print(f"Similarité CLIP: {result['clip_similarity']:.4f}")
            else:
                print("Aucun match CLIP trouvé")
        else:
            result["errors"].append("Échec génération vecteur CLIP")

        # 2. Vérification OCR
        print("Extraction texte et vecteurs OCR...")
        extracted_text, doc_id, embeddings = extract_and_embed(image_path)
        result["extracted_text"] = extracted_text

        if embeddings:
            best_ocr_score = 0.0
            best_ocr_match = None
            for chunk_data in embeddings:
                points = query_qdrant(config["ocr_collection"], chunk_data["embedding"], limit=1)
                if points:
                    match = points[0]
                    if match.get("score", 0) > best_ocr_score:
                        best_ocr_score = match["score"]
                        best_ocr_match = {
                            "id": match["id"],
                            "score": match["score"],
                            "payload": match.get("payload", {}),
                            "chunk_index": chunk_data["chunk_index"]
                        }
            if best_ocr_match:
                result["ocr_similarity"] = best_ocr_score
                result["ocr_match"] = best_ocr_match
                print(f"Meilleure similarité OCR (chunk {best_ocr_match['chunk_index']}): {best_ocr_score:.4f}")
            else:
                print("Aucun match OCR trouvé")
        else:
            result["errors"].append("Échec génération vecteurs OCR")

        # 3. Verdict final : Multi-critères indépendants (CLIP et OCR uniquement)
        clip_ok = result["clip_similarity"] >= result["clip_threshold"]
        ocr_ok = result["ocr_similarity"] >= result["ocr_threshold"]
        
        result["is_valid"] = clip_ok and ocr_ok

        print(f"\n{'='*50}")
        print(f"VERDICT: {'VALIDE' if result['is_valid'] else 'INVALIDE'}")
        print(f"Détails: CLIP={clip_ok} ({result['clip_similarity']:.2f}), "
              f"OCR={ocr_ok} ({result['ocr_similarity']:.2f})")
        print(f"{'='*50}")

        return result

    except Exception as e:
        result["errors"].append(f"Erreur vérification: {e}")
        print(f"Erreur vérification: {e}", file=sys.stderr)
        return result

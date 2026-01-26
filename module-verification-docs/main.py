"""
Script principal pour tester le système de vérification de documents.
"""

import os
import sys
import uuid
import shutil
from pdf2image import convert_from_path

from verification import verify_document, store_reference_vector
from verification.clip import generate_clip_vector
from verification.ocr import extract_and_embed


# =========================
# CONFIG
# =========================
from verification.config import SUPPORTED_DOCUMENT_TYPES
POPPLER_PATH = r"D:\Release-25.12.0-0\poppler-25.12.0\Library\bin"


# =========================
# HELPERS
# =========================
def resolve_path(path: str) -> str:
    """
    Tente de trouver le fichier, soit tel quel, soit dans le dossier 'docs'.
    """
    if not path:
        return None
        
    if os.path.exists(path):
        return os.path.abspath(path)
        
    # Tester dans le dossier 'docs' relatif au script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(script_dir, "docs")
    docs_path = os.path.join(docs_dir, path)
    
    if os.path.exists(docs_path):
        return docs_path
        
    return None


# =========================
# MAIN
# =========================
def main():
    print("=" * 60)
    print("SYSTÈME DE VÉRIFICATION DE DOCUMENTS - CreditSense AI")
    print("=" * 60)

    print("\nChoisissez le type de document:")
    for i, t in enumerate(SUPPORTED_DOCUMENT_TYPES, 1):
        print(f"{i}. {t}")
    
    type_choice = input(f"\nVotre choix (1-{len(SUPPORTED_DOCUMENT_TYPES)}): ").strip()
    try:
        doc_type = SUPPORTED_DOCUMENT_TYPES[int(type_choice) - 1]
    except (ValueError, IndexError):
        print("Choix de type invalide. Utilisation par défaut: CIN")
        doc_type = "CIN"

    print("\nChoisissez un mode:")
    print("1. Stocker un vecteur de référence (manuel)")
    print("2. Vérifier un document")
    print("3. Vérifier → si valide → stocker automatiquement")

    choice = input("\nVotre choix (1/2/3): ").strip()

    if choice == "1":
        path = input(f"Chemin de l'image {doc_type} de référence: ").strip()
        resolved_path = resolve_path(path)
        if resolved_path:
            store_reference_mode(resolved_path, doc_type)
        else:
            print(f"[ERROR] Impossible de trouver le fichier: {path}")

    elif choice == "2":
        verify_mode(doc_type, auto_store=False)

    elif choice == "3":
        verify_mode(doc_type, auto_store=True)

    else:
        print("Choix invalide.")
        sys.exit(1)


# =========================
# STOCKAGE RÉFÉRENCE
# =========================
def store_reference_mode(image_path: str, document_type: str):
    print(f"\nSTOCKAGE DES VECTEURS DE RÉFÉRENCE {document_type}")
    print("-" * 60)

    side = ""
    while side not in ["front", "back"]:
        side = input("C'est le 'front' ou le 'back' du document ? (front/back): ").strip().lower()

    # -------- CLIP --------
    clip_vector = generate_clip_vector(image_path)
    if clip_vector is not None:
        store_reference_vector(
            document_type=document_type,
            vector_type="clip",
            vector=clip_vector,
            point_id=str(uuid.uuid4()),
            metadata={"source": "auto_reference", "type": document_type.lower(), "side": side}
        )
        print("[OK] CLIP stocke")

    # -------- OCR --------
    extracted_text, doc_id, embeddings = extract_and_embed(image_path)
    if embeddings:
        for chunk in embeddings:
            store_reference_vector(
                document_type=document_type,
                vector_type="ocr",
                vector=chunk["embedding"],
                point_id=chunk["point_id"],
                metadata={
                    "doc_id": doc_id,
                    "chunk_index": chunk["chunk_index"],
                    "type": document_type.lower(),
                    "side": side
                }
            )
        print(f"[OK] {len(embeddings)} vecteurs OCR stockes")
    else:
        print("[WARN] Aucun vecteur OCR généré (OCR a peut-être échoué)")


# =========================
# VÉRIFICATION
# =========================
def verify_mode(document_type: str, auto_store: bool = False):
    doc_input = input("\nChemin du document (image ou PDF): ").strip()
    stored_path = resolve_path(doc_input)

    if not stored_path:
        print("Fichier introuvable.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(script_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    filename = os.path.basename(stored_path)
    final_docs_path = os.path.join(docs_dir, filename)

    if stored_path != final_docs_path:
        shutil.copy(stored_path, final_docs_path)
        stored_path = final_docs_path

    print(f"\nDocument stocké sous: {stored_path}")

    # -------- PDF → images --------
    pages = []
    if stored_path.lower().endswith(".pdf"):
        print("Conversion PDF → images...")
        images = convert_from_path(
            stored_path,
            dpi=300,
            poppler_path=POPPLER_PATH
        )
        for i, img in enumerate(images):
            p = os.path.join(docs_dir, f"{filename}_page_{i+1}.png")
            img.save(p)
            pages.append(p)
    else:
        pages.append(stored_path)

    # -------- Vérification --------
    best_result = None

    for page in pages:
        print(f"\nAnalyse: {page}")
        result = verify_document(page, document_type)

        print(f"CLIP: {result['clip_similarity']:.4f}")
        print(f"OCR : {result['ocr_similarity']:.4f}")

        if not best_result or result["ocr_similarity"] > best_result["ocr_similarity"]:
            best_result = result
            best_page = page

    # -------- Verdict --------
    print("\n" + "=" * 60)
    print("VERDICT GLOBAL")
    print("=" * 60)

    if best_result and best_result["is_valid"]:
        print(f"[OK] DOCUMENT RECONNU COMME {document_type}")

        #AUTO-STOCKAGE SI MODE 3
        if auto_store:
            print(f"[INFO] Stockage automatique des vecteurs ({document_type} reconnu)")
            store_reference_mode(best_page, document_type)
    else:
        print(f"[KO] DOCUMENT NON RECONNU COMME {document_type}")

    print("=" * 60)


# =========================
if __name__ == "__main__":
    main()

#si le doc est un cin il le stocke, sinon il le rejète et donc j'ai une base de vecteurs de reference 
#pour les documents valides
#je dois trouver une solution pour qu"il ne charge pas le model plusieurs fois ( safetensors et special_token_map etc )( mettre en cache par exemple)
#je dois aussi trouver une solution pour creer un .env et separer les variables de la config des modèles 


#opencv pour traiter l'image 
#stocker les vecteurs de ref une autre fois
#reessayer sur un document une autre fois 
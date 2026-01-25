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
DOCUMENT_TYPE = "CIN"
POPPLER_PATH = r"D:\Release-25.12.0-0\poppler-25.12.0\Library\bin"


# =========================
# MAIN
# =========================
def main():
    print("=" * 60)
    print("SYSTÈME DE VÉRIFICATION DE DOCUMENTS - CreditSense AI")
    print("=" * 60)

    print("\nChoisissez un mode:")
    print("1. Stocker un vecteur de référence (manuel)")
    print("2. Vérifier un document")
    print("3. Vérifier → si CIN valide → stocker automatiquement")

    choice = input("\nVotre choix (1/2/3): ").strip()

    if choice == "1":
        path = input("Chemin de l'image CIN de référence: ").strip()
        store_reference_mode(path)

    elif choice == "2":
        verify_mode(auto_store=False)

    elif choice == "3":
        verify_mode(auto_store=True)

    else:
        print("Choix invalide.")
        sys.exit(1)


# =========================
# STOCKAGE RÉFÉRENCE
# =========================
def store_reference_mode(image_path: str):
    print("\nSTOCKAGE DES VECTEURS DE RÉFÉRENCE CIN")
    print("-" * 60)

    # -------- CLIP --------
    clip_vector = generate_clip_vector(image_path)
    if clip_vector is not None:
        store_reference_vector(
            document_type=DOCUMENT_TYPE,
            vector_type="clip",
            vector=clip_vector,
            point_id=str(uuid.uuid4()),
            metadata={"source": "auto_reference", "type": "cin"}
        )
        print("✔ CLIP stocké")

    # -------- OCR --------
    extracted_text, doc_id, embeddings = extract_and_embed(image_path)
    for chunk in embeddings:
        store_reference_vector(
            document_type=DOCUMENT_TYPE,
            vector_type="ocr",
            vector=chunk["embedding"],
            point_id=chunk["point_id"],
            metadata={
                "doc_id": doc_id,
                "chunk_index": chunk["chunk_index"],
                "type": "cin"
            }
        )

    print(f"✔ {len(embeddings)} vecteurs OCR stockés")


# =========================
# VÉRIFICATION
# =========================
def verify_mode(auto_store: bool = False):
    doc_input = input("\nChemin du document (image ou PDF): ").strip()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(script_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    # Résolution chemin
    if not os.path.exists(doc_input):
        doc_input = os.path.join(docs_dir, doc_input)
        if not os.path.exists(doc_input):
            print("Fichier introuvable.")
            return

    filename = os.path.basename(doc_input)
    stored_path = os.path.join(docs_dir, filename)

    if doc_input != stored_path:
        shutil.copy(doc_input, stored_path)

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
        result = verify_document(page, DOCUMENT_TYPE)

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
        print("✔ DOCUMENT RECONNU COMME CIN")

        #AUTO-STOCKAGE SI MODE 3
        if auto_store:
            print("➕ Stockage automatique des vecteurs (CIN reconnu)")
            store_reference_mode(best_page)
    else:
        print("✖ DOCUMENT NON CIN / NON RECONNU")

    print("=" * 60)


# =========================
if __name__ == "__main__":
    main()

#si le doc est un cin il le stocke, sinon il le rejète et donc j'ai une base de vecteurs de reference 
#pour les documents valides
#je dois trouver une solution pour qu"il ne charge pas le model plusieurs fois ( safetensors et special_token_map etc )( mettre en cache par exemple)
#je dois aussi trouver une solution pour creer un .env et separer les variables de la config des modèles 

"""
Script principal pour tester le système de vérification de documents.
CreditSense AI
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
POPPLER_PATH = r"D:\Release-25.12.0-0\poppler-25.12.0\Library\bin"

SUPPORTED_DOCS = {
    "1": "CIN",
    "2": "PASSPORT",
    "3": "BTS_LOAN_APP"
}


# =========================
# MAIN
# =========================
def main():
    print("=" * 60)
    print("SYSTÈME DE VÉRIFICATION DE DOCUMENTS - CreditSense AI")
    print("=" * 60)

    print("\nChoisissez un type de document:")
    print("1. CIN")
    print("2. PASSPORT")
    print("3. DEMANDE DE CRÉDIT (BTS_LOAN_APP)")

    doc_choice = input("\nVotre choix (1/2/3): ").strip()
    if doc_choice not in SUPPORTED_DOCS:
        print("Choix invalide.")
        sys.exit(1)

    document_type = SUPPORTED_DOCS[doc_choice]

    print(f"\nMode sélectionné pour: {document_type}")
    print("\nChoisissez une action:")
    print("1. Stocker un vecteur de référence (manuel)")
    print("2. Vérifier un document")
    print("3. Vérifier → si valide → stocker automatiquement")

    action_choice = input("\nVotre choix (1/2/3): ").strip()

    if action_choice == "1":
        path = input(f"Chemin de l'image {document_type} de référence: ").strip()
        store_reference_mode(path, document_type)

    elif action_choice == "2":
        verify_mode(document_type, auto_store=False)

    elif action_choice == "3":
        verify_mode(document_type, auto_store=True)

    else:
        print("Choix invalide.")
        sys.exit(1)


# =========================
# STOCKAGE RÉFÉRENCE
# =========================
def store_reference_mode(image_path: str, document_type: str):
    print(f"\nSTOCKAGE DES VECTEURS DE RÉFÉRENCE [{document_type}]")
    print("-" * 60)

    # -------- Résolution chemin --------
    if not os.path.exists(image_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        docs_dir = os.path.join(script_dir, "docs")
        potential_path = os.path.join(docs_dir, image_path)
        if os.path.exists(potential_path):
            image_path = potential_path
        else:
            print(f"[ERREUR] Fichier introuvable: {image_path}")
            return

    # -------- CLIP --------
    clip_vector = generate_clip_vector(image_path)
    if clip_vector is not None:
        store_reference_vector(
            document_type=document_type,
            vector_type="clip",
            vector=clip_vector,
            point_id=str(uuid.uuid4()),
            metadata={
                "source": "reference",
                "document_type": document_type.lower()
            }
        )
        print("[OK] Vecteur CLIP stocké")
    else:
        print("[ERREUR] Échec de génération du vecteur CLIP")

    # -------- OCR --------
    extracted_text, doc_id, embeddings = extract_and_embed(image_path)
    if embeddings:
        for chunk in embeddings:
            store_reference_vector(
                document_type=document_type,
                vector_type="ocr",
                vector=chunk["embedding"],
                point_id=chunk.get("point_id", str(uuid.uuid4())),
                metadata={
                    "doc_id": doc_id,
                    "chunk_index": chunk["chunk_index"],
                    "document_type": document_type.lower()
                }
            )
        print(f"[OK] {len(embeddings)} vecteurs OCR stockés")
    else:
        print("[ERREUR] Échec de génération des vecteurs OCR")


# =========================
# VÉRIFICATION
# =========================
def verify_mode(document_type: str, auto_store: bool = False):
    doc_input = input(
        f"\nChemin du document {document_type} (image ou PDF): "
    ).strip()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(script_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    # -------- Résolution chemin --------
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
            page_path = os.path.join(
                docs_dir, f"{filename}_page_{i + 1}.png"
            )
            img.save(page_path)
            pages.append(page_path)
    else:
        pages.append(stored_path)

    # -------- Vérification --------
    best_result = None
    best_page = None

    for page in pages:
        print(f"\nAnalyse: {page}")
        result = verify_document(page, document_type)

        print(f"CLIP: {result['clip_similarity']:.4f} "
              f"(Seuil: {result['clip_threshold']})")
        print(f"OCR : {result['ocr_similarity']:.4f} "
              f"(Seuil: {result['ocr_threshold']})")

        if not best_result or result["ocr_similarity"] > best_result["ocr_similarity"]:
            best_result = result
            best_page = page

    # -------- Verdict --------
    print("\n" + "=" * 60)
    print("VERDICT GLOBAL")
    print("=" * 60)

    if best_result and best_result["is_valid"]:
        print(f"[OK] DOCUMENT RECONNU COMME {document_type}")

        if auto_store:
            print("[INFO] Stockage automatique des vecteurs")
            store_reference_mode(best_page, document_type)
    else:
        print(f"[KO] DOCUMENT NON {document_type} / NON RECONNU")

    print("=" * 60)


# =========================
if __name__ == "__main__":
    main()

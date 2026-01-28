import sys
import os

# Add the project root to sys.path to find module-verification-docs
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
module_path = os.path.join(project_root, "module-verification-docs")

if module_path not in sys.path:
    sys.path.append(module_path)

import uuid
import shutil
import json
import argparse
from pdf2image import convert_from_path

try:
    from verification import verify_document, store_reference_vector
    from verification.clip import generate_clip_vector
    from verification.ocr import extract_and_embed
except ImportError as e:
    print(json.dumps({"statut": "erreur", "error": f"Import failed: {str(e)}", "isValid": False}))
    sys.exit(1)


# =========================
# CONFIG
# =========================
POPPLER_PATH = r"D:\Release-25.12.0-0\poppler-25.12.0\Library\bin"

SUPPORTED_DOCS = ["CIN", "PASSPORT", "BTS_LOAN_APP"]


# =========================
# PUBLIC FUNCTION (NEXT.JS)
# =========================
def verify_document_api(
    file_path: str,
    document_type: str,
    auto_store: bool = False
):
    """
    Main entry point for Next.js backend
    """

    if document_type not in SUPPORTED_DOCS:
        raise ValueError(f"Unsupported document type: {document_type}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document not found at: {file_path}")

    pages = []

    # -------- PDF → images --------
    if file_path.lower().endswith(".pdf"):
        images = convert_from_path(
            file_path,
            dpi=300,
            poppler_path=POPPLER_PATH
        )
        for i, img in enumerate(images):
            # Use a temp directory for pages
            temp_dir = os.path.join(project_root, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            page_path = os.path.join(temp_dir, f"{uuid.uuid4()}_page_{i}.png")
            img.save(page_path)
            pages.append(page_path)
    else:
        pages.append(file_path)

    # -------- Verification --------
    best_result = None
    best_page = None

    for page in pages:
        result = verify_document(page, document_type)

        if not best_result or result["ocr_similarity"] > best_result["ocr_similarity"]:
            best_result = result
            best_page = page

    if not best_result:
        return {
            "statut": "rejete",
            "ocrScore": 0,
            "clipScore": 0,
            "isValid": False,
            "error": "Review failed to generate results"
        }

    is_valid = best_result["is_valid"]

    response = {
        "statut": "valide" if is_valid else "rejete",
        "ocrScore": round(best_result["ocr_similarity"] * 100, 2),
        "clipScore": round(best_result["clip_similarity"] * 100, 2),
        "isValid": is_valid
    }

    # -------- Auto-store references --------
    if is_valid and auto_store:
        store_reference_mode(best_page, document_type)

    return response


# =========================
# INTERNAL: STORE REFERENCE
# =========================
def store_reference_mode(image_path: str, document_type: str):
    # -------- CLIP --------
    clip_vector = generate_clip_vector(image_path)
    if clip_vector is not None:
        store_reference_vector(
            document_type=document_type,
            vector_type="clip",
            vector=clip_vector,
            point_id=str(uuid.uuid4()),
            metadata={
                "source": "auto_reference",
                "document_type": document_type.lower()
            }
        )

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


# =========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CreditSense AI Document Verification CLI")
    parser.add_argument("--path", required=True, help="Path to the document file")
    parser.add_argument("--type", required=True, help="Type of document (CIN, PASSPORT, BTS_LOAN_APP)")
    parser.add_argument("--autostore", action="store_true", help="Automatically store as reference if valid")
    
    args = parser.parse_args()
    
    try:
        res = verify_document_api(args.path, args.type, auto_store=args.autostore)
        print(json.dumps(res))
    except Exception as e:
        print(json.dumps({
            "statut": "erreur",
            "error": str(e),
            "isValid": False
        }))

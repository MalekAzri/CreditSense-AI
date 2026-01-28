"""
Module OCR: Extraction de texte et génération d'embeddings textuels avec chunking.
Chaque chunk de texte est relié au même document via document_id.
"""

import re
import sys
import uuid

# IMPORTANT: Importer config en premier pour configurer HF_HOME
from . import config

import pytesseract
from sentence_transformers import SentenceTransformer
from .utils import load_image, preprocess_image_for_ocr
from .config import (
    TEXT_EMBEDDING_MODEL_ID,
    TESSERACT_CONFIG,
    TESSERACT_LANG,
    OCR_UPSCALE_FACTOR,
    MODELS_LOCAL_FILES_ONLY,
)

# =========================
# CACHE GLOBAL DU MODÈLE
# =========================
_text_embedding_model = None


def get_text_embedding_model():
    """
    Charge le modèle SentenceTransformer UNE SEULE FOIS
    (singleton en mémoire)
    """
    global _text_embedding_model

    if _text_embedding_model is None:
        print(
            f"[CACHE] Chargement du modèle OCR embedding "
            f"{TEXT_EMBEDDING_MODEL_ID} (local_only={MODELS_LOCAL_FILES_ONLY})"
        )

        _text_embedding_model = SentenceTransformer(
            TEXT_EMBEDDING_MODEL_ID
            # SentenceTransformer utilise automatiquement HF_HOME / cache HF
        )

    return _text_embedding_model


def extract_text_from_image(image_path: str, lang: str = TESSERACT_LANG) -> str:
    try:
        image = load_image(image_path)
        processed_image = preprocess_image_for_ocr(
            image, upscale_factor=OCR_UPSCALE_FACTOR
        )

        raw_text = pytesseract.image_to_string(
            processed_image,
            lang=lang,
            config=TESSERACT_CONFIG,
        )

        cleaned_lines = []
        for line in raw_text.splitlines():
            cleaned_line = re.sub(r"[^\u0600-\u06FF\s]", "", line).strip()
            if cleaned_line:
                cleaned_lines.append(cleaned_line)

        return "\n".join(cleaned_lines)

    except Exception as e:
        print(f"Erreur OCR: {e}", file=sys.stderr)
        return ""


def generate_text_embedding(text: str):
    if not text or not text.strip():
        return None

    try:
        model = get_text_embedding_model()
        return model.encode(text)

    except Exception as e:
        print(f"Erreur embedding OCR: {e}", file=sys.stderr)
        return None


def chunk_text(text: str, max_words: int = 100):
    words = text.split()
    return [
        " ".join(words[i : i + max_words])
        for i in range(0, len(words), max_words)
    ]


def extract_and_embed(image_path: str, lang: str = TESSERACT_LANG):
    text = extract_text_from_image(image_path, lang)
    if not text:
        return "", None, None

    document_id = str(uuid.uuid4())
    chunks = chunk_text(text, max_words=100)

    embeddings = []
    for idx, chunk in enumerate(chunks):
        emb = generate_text_embedding(chunk)
        if emb is not None:
            embeddings.append(
                {
                    "point_id": str(uuid.uuid4()),
                    "chunk_index": idx,
                    "embedding": emb,
                    "text_preview": chunk[:100],
                }
            )

    if not embeddings:
        return text, document_id, None

    return text, document_id, embeddings

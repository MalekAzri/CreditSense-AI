import os
from dotenv import load_dotenv

# Charger le fichier .env depuis la racine du projet
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

# ========== QDRANT ==========
QDRANT_USE_CLOUD = os.getenv("QDRANT_USE_CLOUD", "False").lower() == "true"
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_CLOUD_URL = os.getenv("QDRANT_CLOUD_URL", "")
QDRANT_CLOUD_API_KEY = os.getenv("QDRANT_CLOUD_API_KEY", "")

# ========== HuggingFace ==========
HF_CACHE_DIR = os.getenv("HF_CACHE_DIR", r"D:\CreditSense Ai\huggingface_cache")
MODELS_LOCAL_FILES_ONLY = os.getenv("MODELS_LOCAL_FILES_ONLY", "False").lower() == "true"

# ========== Modèles ==========
CLIP_MODEL_ID = "openai/clip-vit-base-patch32"
TEXT_EMBEDDING_MODEL_ID = "paraphrase-multilingual-MiniLM-L12-v2"

# ========== Collections Qdrant ==========
QDRANT_COLLECTIONS = {
    "CIN": {
        "clip_collection": "cin_clip_vectors",
        "ocr_collection": "cin_ocr_vectors",
        "vector_size_clip": 512,
        "vector_size_ocr": 384,
    },
    "PASSPORT": {
        "clip_collection": "passport_clip_vectors",
        "ocr_collection": "passport_ocr_vectors",
        "vector_size_clip": 512,
        "vector_size_ocr": 384,
    },
    "BTS_LOAN_APP": {
        "clip_collection": "bts_loan_app_clip_vectors",
        "ocr_collection": "bts_loan_app_ocr_vectors",
        "vector_size_clip": 512,
        "vector_size_ocr": 384,
    }
}

# ========== Seuils ==========
SIMILARITY_THRESHOLDS = {
    "CIN": {"clip_threshold": 0.70, "ocr_threshold": 0.70},
    "PASSPORT": {"clip_threshold": 0.70, "ocr_threshold": 0.70},
    "BTS_LOAN_APP": {"clip_threshold": 0.70, "ocr_threshold": 0.70},
}

# ========== OCR ==========
TESSERACT_CONFIG = r'--oem 3 --psm 6'
TESSERACT_LANG = 'ara'
OCR_UPSCALE_FACTOR = 3

# ========== Types supportés ==========
SUPPORTED_DOCUMENT_TYPES = ["CIN", "PASSPORT", "BTS_LOAN_APP"]

# ========== Fonctions utilitaires ==========
def get_collection_config(document_type: str):
    if document_type not in QDRANT_COLLECTIONS:
        raise ValueError(f"Type non supporté: {document_type}")
    return QDRANT_COLLECTIONS[document_type]

def get_similarity_thresholds(document_type: str):
    if document_type not in SIMILARITY_THRESHOLDS:
        raise ValueError(f"Type non supporté: {document_type}")
    return SIMILARITY_THRESHOLDS[document_type]

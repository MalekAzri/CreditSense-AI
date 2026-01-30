"""
Configuration centrale du module audio CreditSense AI
"""
import os
from pathlib import Path

# === Chemins de base ===
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Racine du projet audio_module/
AUDIO_STORAGE_PATH = BASE_DIR / "audio_storage"

# === Base de données ===
DATABASE_URL = f"sqlite:///{BASE_DIR}/audio_module.db"

# === Redis (pour Celery) ===
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# === Celery ===
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# === Paramètres audio (WhatsApp) ===
# WhatsApp envoie principalement des fichiers OGG (Opus codec), mais peut aussi envoyer MP3/M4A
ALLOWED_AUDIO_EXTENSIONS = {".ogg", ".mp3", ".m4a"}
MAX_AUDIO_FILE_SIZE_MB = 16  # WhatsApp limite les vocaux à 16MB

# === Qdrant Cloud (Base de données vectorielle) ===
QDRANT_URL = "https://c357d8e2-87a6-4ab0-9a72-4518ea62f52a.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.5Y7xA-IKk5V5tE_-vfqy9ZZpCOXFbVFQl-cbuJPNSKE"
QDRANT_COLLECTION_NAME = "audio_embeddings"
QDRANT_VECTOR_SIZE = 384

# === Création automatique des dossiers nécessaires ===
def init_directories():
    """Crée les dossiers requis s'ils n'existent pas"""
    AUDIO_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    print(f"✅ Dossier audio_storage créé : {AUDIO_STORAGE_PATH}")

# Appel automatique à l'import
init_directories()
# Gère la configuration de l'application (variables d'environnement, paramètres globaux).
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

# === Création automatique des dossiers nécessaires ===
def init_directories():
    """Crée les dossiers requis s'ils n'existent pas"""
    AUDIO_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    print(f"✅ Dossier audio_storage créé : {AUDIO_STORAGE_PATH}")

# Appel automatique à l'import
init_directories()
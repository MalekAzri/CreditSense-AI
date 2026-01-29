
import sys
import os
import hashlib
from pathlib import Path

# Ajouter le répertoire parent au path pour importer app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.base import SessionLocal
from app.db.models import Audio
from app.services.qdrant_service import get_qdrant_service

def check_embedding(audio_id=None):
    """
    Vérifie les données pour un audio donné ou les 3 derniers.
    """
    db = SessionLocal()
    qdrant = get_qdrant_service()
    
    try:
        audios = []
        if audio_id:
            found = db.query(Audio).filter(Audio.id == audio_id).first()
            if not found:
                print(f"❌ Audio ID {audio_id} introuvable.")
                return
            audios = [found]
        else:
            # Prendre les 3 derniers avec métadonnées
            audios = db.query(Audio).order_by(Audio.id.desc()).limit(3).all()
            if not audios:
                print("⚠️  Aucun audio trouvé.")
                return
            print(f"ℹ️  Analyse des {len(audios)} derniers audios...")

        for audio in audios:
            print(f"\n{'='*50}")
            print(f"🔍 Analyse pour Audio ID {audio.id} ({audio.filename})")
            
            # Transcription
            if audio.transcription:
                print(f"   📝 Transcription : \"{audio.transcription.text[:100]}...\"")
                print(f"      Langue : {audio.transcription.language} | Confiance : {audio.transcription.confidence}")
            else:
                print("   ⚠️ Pas de transcription trouvée.")

            # Processing Info (Raw Features)
            if audio.processing_info:
                info = audio.processing_info
                print(f"   📊 Features & Scores:")
                print(f"      - Sentiment: {info.sentiment_score}")
                print(f"      - Stress: {info.stress_level} | Confiance: {info.confidence_level}")
                print(f"      --- RAW FEATURES ---")
                print(f"      - Duration/Checksum: (See Celery Logs)")
                print(f"      - Energy (dB): {info.energy_db}")
                print(f"      - Pause Rate: {info.pause_rate}")
                print(f"      - Speech Rate: {info.speech_rate}")
                print(f"      - Pitch Mean: {info.pitch_mean}")
            else:
                print("   ⚠️ Pas de métadonnées de traitement.")

            # Vérification du fichier physique (MD5 pour voir si ce sont les mêmes fichiers)
            file_path = Path(audio.file_path)
            if file_path.exists():
                size = file_path.stat().st_size
                md5_hash = hashlib.md5()
                with open(file_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        md5_hash.update(byte_block)
                md5_digest = md5_hash.hexdigest()
                print(f"   📂 Fichier physique: {file_path.name}")
                print(f"      Taille: {size} bytes | MD5: {md5_digest}")
            else:
                print(f"   ❌ Fichier physique INTROUVABLE: {audio.file_path}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            aid = int(sys.argv[1])
            check_embedding(aid)
        except ValueError:
            print("⚠️  L'argument doit être un ID (nombre entier).")
    else:
        check_embedding()


import sys
import os
from pathlib import Path
from sqlalchemy.orm import Session

# Ajouter le répertoire parent au path pour importer app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.base import SessionLocal
from app.db.models import Audio, Transcription, ProcessingMetadata
from app.services.qdrant_service import get_qdrant_service
from app.core.config import AUDIO_STORAGE_PATH

def clear_storage():
    print("🗑️  Démarrage du nettoyage du stockage audio et de la base de données...")
    
    db: Session = SessionLocal()
    qdrant = get_qdrant_service()
    
    try:
        # 1. Récupérer tous les audios
        audios = db.query(Audio).all()
        print(f"📋 {len(audios)} enregistrements audio trouvés dans la base de données.")
        
        deleted_count = 0
        
        for audio in audios:
            print(f"\nTraitement Audio ID {audio.id} ({audio.filename})...")
            
            # A. Supprimer de Qdrant
            if audio.qdrant_point_id:
                try:
                    # Tenter de convertir en int si c'est possible, sinon garder tel quel (le service attend un int mais le modèle stocke un str)
                    point_id = int(audio.qdrant_point_id) if audio.qdrant_point_id.isdigit() else audio.qdrant_point_id
                    # Note: delete_audio_vector attend un int (audio_id) dans le code actuel du service
                    # Mais l'audio.id est utilisé comme point_id.
                    # On va utiliser audio.id pour être sûr car insert_audio_vector utilise audio_id comme point_id.
                    qdrant.delete_audio_vector(audio.id)
                except Exception as e:
                    print(f"⚠️  Erreur suppression Qdrant : {e}")
            
            # B. Supprimer le fichier physique
            file_path = Path(audio.file_path)
            if file_path.exists():
                try:
                    os.remove(file_path)
                    print(f"✅ Fichier supprimé : {file_path}")
                except Exception as e:
                    print(f"❌ Erreur suppression fichier {file_path} : {e}")
            else:
                print(f"⚠️  Fichier introuvable sur le disque : {file_path}")
            
            # C. Supprimer les dépendances (Cascade ou manuel)
            # SQLAlchemy gère souvent ça si configuré, sinon on le fait manuellement pour être sûr
            db.query(Transcription).filter(Transcription.audio_id == audio.id).delete()
            db.query(ProcessingMetadata).filter(ProcessingMetadata.audio_id == audio.id).delete()
            
            # D. Supprimer l'enregistrement Audio
            db.delete(audio)
            deleted_count += 1
            
        db.commit()
        print(f"\n✨ Nettoyage DB terminé : {deleted_count} entrées supprimées.")
        
        # 2. Nettoyage des fichiers orphelins dans audio_storage
        print("\n🧹 Vérification des fichiers orphelins dans audio_storage...")
        if AUDIO_STORAGE_PATH.exists():
            for file in AUDIO_STORAGE_PATH.iterdir():
                if file.is_file():
                    try:
                        os.remove(file)
                        print(f"🗑️  Fichier orphelin supprimé : {file}")
                    except Exception as e:
                        print(f"❌ Erreur suppression orphelin {file} : {e}")
        
    except Exception as e:
        print(f"\n❌ Une erreur est survenue : {e}")
        db.rollback()
    finally:
        db.close()
        print("\n🏁 Opération terminée.")

if __name__ == "__main__":
    confirm = input("⚠️  ATTENTION : Cela va supprimer TOUS les fichiers audio et les données associées. Continuer ? (oui/non) : ")
    if confirm.lower() in ["oui", "yes", "y"]:
        clear_storage()
    else:
        print("Annulé.")

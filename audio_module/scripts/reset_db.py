
import sys
import os
import time
from pathlib import Path
from sqlalchemy import create_engine

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.config import DATABASE_URL
from app.db.base import Base
from app.db.models import * # Import all models to ensure they are registered

def reset_database():
    print("🔄 Tentative de réinitialisation de la base de données...")
    
    # Extraire le chemin du fichier depuis l'URL (sqlite:///...)
    if "sqlite" in DATABASE_URL:
        db_path_str = DATABASE_URL.replace("sqlite:///", "")
        db_path = Path(db_path_str)
        
        if db_path.exists():
            print(f"   Fichier trouvé : {db_path}")
            try:
                os.remove(db_path)
                print("   ✅ Fichier supprimé avec succès.")
            except PermissionError:
                print("   ❌ ERREUR : Le fichier est verrouillé par un autre processus.")
                print("   ⚠️  Veuillez arrêter Uvicorn, Celery et tout autre outil utilisant la DB.")
                return False
            except Exception as e:
                print(f"   ❌ Erreur inattendue lors de la suppression : {e}")
                return False
        else:
            print("   ℹ️  Le fichier n'existe pas encore (c'est normal).")
            
        # Re-création
        try:
            print("   🛠️  Création des nouvelles tables...")
            engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(bind=engine)
            print("   ✅ Tables créées avec succès (Nouveau Schéma Appliqué).")
            return True
        except Exception as e:
            print(f"   ❌ Erreur lors de la création des tables : {e}")
            return False
    else:
        print("   ❌ Ce script ne gère que SQLite pour le moment.")
        return False

if __name__ == "__main__":
    confirm = input("⚠️  ATTENTION : Cela va supprimer toute la base de données. Continuer ? (oui/non) : ")
    if confirm.lower() in ["oui", "yes", "y"]:
        if reset_database():
            print("\n🏁 Base de données réinitialisée. Vous pouvez redémarrer vos workers.")
        else:
            print("\n❌ Échec de la réinitialisation.")
            sys.exit(1)
    else:
        print("Annulé.")

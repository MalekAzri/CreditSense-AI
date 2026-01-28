# Gère la session de base de données (connexion, pool).
"""
Gestion des sessions de base de données
"""
from app.db.base import SessionLocal

def get_db():
    """
    Dependency pour obtenir une session DB dans FastAPI
    Utilisée comme : db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
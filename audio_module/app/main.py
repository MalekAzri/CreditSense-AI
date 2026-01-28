# Point d'entrée principal de l'application (FastAPI/Flask app instantiation).
"""
Point d'entrée principal de l'application FastAPI
"""
from fastapi import FastAPI
from app.api.audio import router as audio_router
from app.db.base import engine, Base
from app.db import models  # Import nécessaire pour que SQLAlchemy connaisse les modèles

# Créer les tables dans la base de données
Base.metadata.create_all(bind=engine)

# Initialiser l'application FastAPI
app = FastAPI(
    title="CreditSense AI - Audio Module",
    description="Module d'analyse comportementale audio WhatsApp avec Qdrant",
    version="0.1.0"
)

# Inclure les routes
app.include_router(audio_router, prefix="/api/audio", tags=["audio"])


@app.get("/")
def root():
    """
    Route racine
    """
    return {
        "message": "CreditSense AI - Audio Module",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """
    Health check global de l'application
    """
    return {
        "status": "ok",
        "service": "audio_module",
        "message": "Service is running"
    }
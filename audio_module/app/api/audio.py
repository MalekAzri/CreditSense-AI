# Définit les endpoints de l'API pour la gestion et le traitement audio.

"""
Routes API pour le module audio
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict
import os
import uuid
from pathlib import Path
from datetime import datetime

from app.db.session import get_db
from app.db.models import Audio, AudioStatus
from app.core.config import AUDIO_STORAGE_PATH, ALLOWED_AUDIO_EXTENSIONS, MAX_AUDIO_FILE_SIZE_MB

router = APIRouter()


@router.get("/health")
def health_check() -> Dict[str, str]:
    """
    Vérification de santé du module audio
    """
    return {
        "status": "ok",
        "module": "audio",
        "message": "Audio module is ready"
    }


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    whatsapp_message_id: str = None,
    whatsapp_phone_number: str = None,
    whatsapp_profile_name: str = None,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload d'un fichier audio depuis WhatsApp
    
    Args:
        file: Fichier audio (OGG, MP3, M4A)
        whatsapp_message_id: ID du message WhatsApp (optionnel)
        whatsapp_phone_number: Numéro du client (optionnel, peut être anonymisé)
        whatsapp_profile_name: Nom du profil WhatsApp (optionnel)
        db: Session de base de données
    
    Returns:
        dict avec audio_id et statut
    """
    
    # 1. Validation de l'extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté. Formats acceptés : {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        )
    
    # 2. Lecture du fichier
    file_content = await file.read()
    file_size_bytes = len(file_content)
    
    # 3. Validation de la taille
    max_size_bytes = MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux. Taille max : {MAX_AUDIO_FILE_SIZE_MB} MB"
        )
    
    # 4. Génération d'un nom unique
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = AUDIO_STORAGE_PATH / unique_filename
    
    # 5. Sauvegarde du fichier
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la sauvegarde du fichier : {str(e)}"
        )
    
    # 6. Création de l'entrée dans la base de données
    audio_entry = Audio(
        filename=file.filename,
        format=file_extension.replace(".", ""),
        file_path=str(file_path),
        file_size_bytes=file_size_bytes,
        whatsapp_message_id=whatsapp_message_id,
        whatsapp_phone_number=whatsapp_phone_number,
        whatsapp_profile_name=whatsapp_profile_name,
        status=AudioStatus.UPLOADED,
        upload_date=datetime.utcnow()
    )
    
    try:
        db.add(audio_entry)
        db.commit()
        db.refresh(audio_entry)
    except Exception as e:
        # Si erreur DB, supprimer le fichier sauvegardé
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'enregistrement en base de données : {str(e)}"
        )
    
    return {
        "status": "success",
        "message": "Audio uploadé avec succès",
        "audio_id": audio_entry.id,
        "filename": file.filename,
        "size_bytes": file_size_bytes,
        "format": file_extension.replace(".", ""),
        "upload_date": audio_entry.upload_date.isoformat()
    }


@router.get("/status/{audio_id}")
def get_audio_status(audio_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Récupère le statut du traitement d'un audio
    
    Args:
        audio_id: ID de l'audio
        db: Session de base de données
    
    Returns:
        Statut de traitement de l'audio
    """
    audio = db.query(Audio).filter(Audio.id == audio_id).first()
    
    if not audio:
        raise HTTPException(status_code=404, detail="Audio non trouvé")
    
    return {
        "audio_id": audio.id,
        "filename": audio.filename,
        "status": audio.status.value,
        "upload_date": audio.upload_date.isoformat(),
        "processing_started_at": audio.processing_started_at.isoformat() if audio.processing_started_at else None,
        "processing_completed_at": audio.processing_completed_at.isoformat() if audio.processing_completed_at else None
    }


@router.get("/results/{audio_id}")
def get_audio_results(audio_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Récupère les résultats d'analyse d'un audio
    
    Args:
        audio_id: ID de l'audio
        db: Session de base de données
    
    Returns:
        Résultats d'analyse (transcription, sentiment, scoring)
    """
    audio = db.query(Audio).filter(Audio.id == audio_id).first()
    
    if not audio:
        raise HTTPException(status_code=404, detail="Audio non trouvé")
    
    if audio.status != AudioStatus.COMPLETED:
        return {
            "audio_id": audio.id,
            "status": audio.status.value,
            "message": "Traitement non terminé",
            "results": None
        }
    
    # Récupérer la transcription et les métadonnées
    transcription = audio.transcription
    processing_info = audio.processing_info
    
    return {
        "audio_id": audio.id,
        "status": audio.status.value,
        "transcription": {
            "text": transcription.text if transcription else None,
            "language": transcription.language if transcription else None,
            "confidence": transcription.confidence if transcription else None
        } if transcription else None,
        "analysis": {
            "sentiment_score": processing_info.sentiment_score if processing_info else None,
            "stress_level": processing_info.stress_level if processing_info else None,
            "confidence_level": processing_info.confidence_level if processing_info else None,
            "coherence_score": processing_info.coherence_score if processing_info else None,
            "solvability_score": processing_info.solvability_score if processing_info else None,
            "similar_profiles_count": processing_info.similar_profiles_count if processing_info else None
        } if processing_info else None
    }


@router.get("/list")
def list_audios(
    skip: int = 0,
    limit: int = 10,
    status: str = None,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Liste les audios uploadés (avec pagination)
    
    Args:
        skip: Nombre d'enregistrements à sauter
        limit: Nombre maximum d'enregistrements à retourner
        status: Filtrer par statut (optionnel)
        db: Session de base de données
    
    Returns:
        Liste des audios avec métadonnées
    """
    query = db.query(Audio)
    
    # Filtrer par statut si spécifié
    if status:
        try:
            status_enum = AudioStatus(status)
            query = query.filter(Audio.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Statut invalide : {status}")
    
    # Pagination
    total = query.count()
    audios = query.order_by(Audio.upload_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "audios": [
            {
                "audio_id": audio.id,
                "filename": audio.filename,
                "format": audio.format,
                "status": audio.status.value,
                "upload_date": audio.upload_date.isoformat(),
                "whatsapp_phone_number": audio.whatsapp_phone_number
            }
            for audio in audios
        ]
    }
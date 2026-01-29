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
from app.workers.audio_worker import process_audio
from app.db.session import get_db
from app.db.models import Audio, AudioStatus
from app.core.config import AUDIO_STORAGE_PATH, ALLOWED_AUDIO_EXTENSIONS, MAX_AUDIO_FILE_SIZE_MB
from app.services.qdrant_service import get_qdrant_service

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
    # 7. Déclencher le traitement asynchrone avec Celery
    process_audio.delay(audio_entry.id)
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

@router.post("/predict")
async def predict_score(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Prédit le score de solvabilité d'un nouveau fichier basé sur les 5 voisins les plus proches (k-NN)
    Le fichier est traité à la volée mais NON ENREGISTRÉ en base de données de manière permanente.
    """
    from app.services.audio_processing import get_audio_processor
    
    # 1. Validation basique
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté. Formats acceptés : {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        )
    
    # 2. Sauvegarde temporaire du fichier pour traitement
    temp_filename = f"temp_predict_{uuid.uuid4()}{file_extension}"
    temp_path = AUDIO_STORAGE_PATH / temp_filename
    
    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
            
        # 3. Traitement complet (Extraction features + Embedding)
        processor = get_audio_processor()
        # On utilise process_complete qui fait tout (transcription, features, embedding)
        results = processor.process_complete(str(temp_path))
        
        # 4. Récupérer le vecteur généré
        target_vector = results["embedding"]
        
        # 5. Interroger Qdrant
        qdrant = get_qdrant_service()
        similar_audios = qdrant.search_similar_audios(
            query_vector=target_vector,
            limit=5, # On prend les 5 plus proches (pas besoin d'exclure soi-même car on n'est pas en base)
            score_threshold=0.5 
        )
        
        if not similar_audios:
            return {
                "filename": file.filename,
                "prediction_status": "insufficient_data",
                "message": "Aucun voisin similaire trouvé.",
                "predicted_scores": None
            }

        # 6. Calculer la moyenne des scores des voisins
        def get_avg(key, default=0.0):
            values = [n["metadata"].get(key, default) for n in similar_audios]
            # Filtrer les None
            valid_values = [v for v in values if v is not None]
            return sum(valid_values) / len(valid_values) if valid_values else default

        avg_stress = get_avg("stress_level", 0.5)
        avg_confidence = get_avg("confidence_level", 0.5)
        avg_sentiment = get_avg("sentiment_score", 0.0)
        avg_coherence = get_avg("coherence_score", 0.5)
        
        # Features acoustiques moyennes
        avg_pitch = get_avg("pitch_mean", 0.0)
        avg_energy = get_avg("energy_db", -20.0)
        avg_speech = get_avg("speech_rate", 120.0)
        avg_pause = get_avg("pause_rate", 0.1)
        
        print(f"\n🔮 PRÉDICTION TERMINÉE")
        print(f"   Voisins utilisés : {len(similar_audios)}")
        print(f"   Stress Prédit    : {avg_stress:.2f}")
        print(f"   Confiance Prédite: {avg_confidence:.2f}")
        print(f"   Sentiment Prédit : {avg_sentiment:.2f}")
        
        # Formater la réponse
        neighbors_details = [
            {
                "audio_id": n["audio_id"],
                "similarity": n["similarity_score"],
                "stress": n["metadata"].get("stress_level"),
                "confidence": n["metadata"].get("confidence_level"),
                "features": {
                    "pitch_mean": n["metadata"].get("pitch_mean"),
                    "energy_db": n["metadata"].get("energy_db"),
                    "speech_rate": n["metadata"].get("speech_rate"),
                    "pause_rate": n["metadata"].get("pause_rate")
                }
            }
            for n in similar_audios
        ]
        
        # Scores de ce fichier (calculés par l'algo, pas prédits)
        current_file_scores = {
            "stress_level": results["behavioral_scores"]["stress_level"],
            "confidence_level": results["behavioral_scores"]["confidence_level"],
            "sentiment_score": results["sentiment"]["sentiment_score"]
        }
        
        return {
            "prediction_status": "success",
            "neighbors_count": len(similar_audios),
            "current_analysis": current_file_scores, # Les scores basés sur l'algo classique
            "predicted_scores": {
                "stress_level": avg_stress,
                "confidence_level": avg_confidence,
                "sentiment_score": avg_sentiment,
                "coherence_score": avg_coherence,
                "creditworthiness_probability": avg_confidence * (1 - avg_stress),
                "acoustic_averages": {
                    "pitch_mean": avg_pitch,
                    "energy_db": avg_energy,
                    "speech_rate": avg_speech,
                    "pause_rate": avg_pause
                }
            },
            "target_audio_features": {
                 "pitch_mean": results["acoustic_features"]["pitch_mean"],
                 "energy_db": results["acoustic_features"]["energy_db"],
                 "speech_rate": results["acoustic_features"]["speech_rate"],
                 "pause_rate": results["acoustic_features"]["pause_rate"]
            },
            "nearest_neighbors": neighbors_details
        }
        
    except Exception as e:
        print(f"❌ Erreur prédiction : {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 7. Nettoyage du fichier temporaire
        if temp_path.exists():
            try:
                os.remove(temp_path)
            except:
                pass

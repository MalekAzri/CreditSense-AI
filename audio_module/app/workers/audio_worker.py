# app/workers/audio_worker.py
import time
from datetime import datetime
from pathlib import Path

from app.core.celery_app import celery_app
from app.db.base import SessionLocal
from app.db.models import Audio, AudioStatus, Transcription, ProcessingMetadata
from app.services.audio_processing import get_audio_processor
from app.services.qdrant_service import get_qdrant_service

# Force l'initialisation de Qdrant au démarrage du worker
print("🔄 Initialisation de Qdrant...")
_qdrant = get_qdrant_service()
print("✅ Qdrant initialisé")


@celery_app.task(
    bind=True,
    name="process_audio",
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3}
)
def process_audio(self, audio_id: int):
    """
    Tâche asynchrone : traiter un fichier audio
    
    Pipeline complet :
    1. Transcription (Whisper)
    2. Features acoustiques (librosa)
    3. Analyse sentiment
    4. Calcul scores comportementaux
    5. Génération embedding pour Qdrant
    6. Sauvegarde en base de données
    
    Args:
        audio_id: ID de l'audio à traiter
    
    Returns:
        dict avec le résultat du traitement
    """
    db = SessionLocal()
    start_time = time.time()

    try:
        # 1. Récupérer l'audio
        audio = db.query(Audio).filter(Audio.id == audio_id).first()
        if not audio:
            return {"status": "error", "message": f"Audio {audio_id} non trouvé"}

        # Vérifier que le fichier existe
        audio_path = Path(audio.file_path).resolve()
        if not audio_path.exists():
            raise FileNotFoundError(f"Fichier audio introuvable : {audio_path}")

        # 2. Marquer comme "en cours de traitement"
        audio.status = AudioStatus.PROCESSING
        audio.processing_started_at = datetime.utcnow()
        db.commit()

        print(f"\n{'='*70}")
        print(f"🔄 DÉBUT TRAITEMENT AUDIO {audio_id}")
        print(f"   Fichier : {audio.filename}")
        print(f"   Chemin  : {audio.file_path}")
        print(f"{'='*70}\n")

        # 3. Charger le processeur audio
        processor = get_audio_processor()

        # 4. PIPELINE COMPLET DE TRAITEMENT
        results = processor.process_complete(str(audio_path))

        # 5. Sauvegarder la transcription
        transcription = Transcription(
            audio_id=audio.id,
            text=results["transcription"]["text"],
            language=results["transcription"]["language"],
            confidence=1.0
        )
        db.add(transcription)

        # 6. Sauvegarder les métadonnées et analyses
        processing_metadata = ProcessingMetadata(
            audio_id=audio.id,
            sentiment_score=results["sentiment"]["sentiment_score"],
            stress_level=results["behavioral_scores"]["stress_level"],
            confidence_level=results["behavioral_scores"]["confidence_level"],
            coherence_score=results["behavioral_scores"]["coherence_score"],
            pitch_mean=results["acoustic_features"]["pitch_mean"],
            speech_rate=results["acoustic_features"]["speech_rate"],
            pause_rate=results["acoustic_features"]["pause_rate"],
            energy_db=results["acoustic_features"]["energy_db"],
            processing_time_seconds=time.time() - start_time
        )
        db.add(processing_metadata)

        # 7. INSÉRER LE VECTEUR DANS QDRANT
        try:
            # Préparer les métadonnées pour Qdrant
            qdrant_metadata = {
                "language": results["transcription"]["language"],
                "sentiment_score": results["sentiment"]["sentiment_score"],
                "stress_level": results["behavioral_scores"]["stress_level"],
                "confidence_level": results["behavioral_scores"]["confidence_level"],
                "coherence_score": results["behavioral_scores"]["coherence_score"],
                "upload_date": audio.upload_date.isoformat(),
                "outcome": "unknown"  # À labeliser manuellement plus tard
            }

            # Insérer dans Qdrant
            point_id = _qdrant.insert_audio_vector(
                audio_id=audio.id,
                vector=results["embedding"],
                metadata=qdrant_metadata
            )

            # Sauvegarder l'ID du point Qdrant (dans le try)
            audio.qdrant_point_id = str(point_id)

        except Exception as qdrant_error:
            print(f"⚠️ Erreur Qdrant (non bloquante) : {qdrant_error}")
            # On ne bloque pas le traitement si Qdrant échoue
            audio.qdrant_point_id = None

        # 8. Marquer l'audio comme "terminé"
        audio.status = AudioStatus.COMPLETED
        audio.processing_completed_at = datetime.utcnow()

        # 9. Commit final
        db.commit()

        processing_time = time.time() - start_time

        print(f"\n{'='*70}")
        print(f"✅ TRAITEMENT TERMINÉ - Audio {audio_id}")
        print(f"   ⏱️ Temps total     : {processing_time:.2f}s")
        print(f"   🌍 Langue          : {results['transcription']['language']}")
        print(f"   📝 Transcription   : {results['transcription']['text'][:100]}...")
        print(f"   😊 Sentiment       : {results['sentiment']['sentiment_score']:.2f}")
        print(f"   😰 Stress          : {results['behavioral_scores']['stress_level']:.2f}")
        print(f"   💬 Confiance       : {results['behavioral_scores']['confidence_level']:.2f}")
        print(f"{'='*70}\n")

        return {
            "status": "success",
            "audio_id": audio_id,
            "processing_time": processing_time,
            "language": results["transcription"]["language"],
            "sentiment_score": results["sentiment"]["sentiment_score"],
            "stress_level": results["behavioral_scores"]["stress_level"],
            "confidence_level": results["behavioral_scores"]["confidence_level"]
        }

    except Exception as e:
        # En cas d'erreur, marquer comme "échoué"
        print(f"\n{'='*70}")
        print(f"❌ ERREUR TRAITEMENT AUDIO {audio_id}")
        print(f"   Erreur : {str(e)}")
        print(f"{'='*70}\n")

        if audio:
            audio.status = AudioStatus.FAILED
            audio.processing_completed_at = datetime.utcnow()
            db.commit()

        return {
            "status": "error",
            "audio_id": audio_id,
            "message": str(e)
        }

    finally:
        db.close()


@celery_app.task(name="test_task")
def test_task(message: str):
    """
    Tâche de test simple pour vérifier que Celery fonctionne
    """
    print(f"📨 Tâche de test reçue : {message}")
    time.sleep(2)
    print(f"✅ Tâche de test terminée : {message}")
    return {"status": "success", "message": message}
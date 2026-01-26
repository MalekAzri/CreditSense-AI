# app/workers/audio_worker.py
import time
from datetime import datetime
from pathlib import Path

from app.core.celery_app import celery_app
from app.db.base import SessionLocal
from app.db.models import Audio, AudioStatus, Transcription, ProcessingMetadata
from app.services.audio_processing import get_audio_processor
from app.services.qdrant_service import get_qdrant_service

_qdrant = get_qdrant_service()


@celery_app.task(
    bind=True,
    name="process_audio",
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3}
)
def process_audio(self, audio_id: int):
    db = SessionLocal()
    start = time.time()

    try:
        audio = db.query(Audio).filter(Audio.id == audio_id).first()
        if not audio:
            raise ValueError("Audio introuvable")

        audio_path = Path(audio.file_path).resolve()
        if not audio_path.exists():
            raise FileNotFoundError(audio_path)

        audio.status = AudioStatus.PROCESSING
        audio.processing_started_at = datetime.utcnow()
        db.commit()

        processor = get_audio_processor()
        results = processor.process_complete(str(audio_path))

        db.add(Transcription(
            audio_id=audio.id,
            text=results["transcription"]["text"],
            language=results["transcription"]["language"],
            confidence=1.0
        ))

        db.add(ProcessingMetadata(
            audio_id=audio.id,
            sentiment_score=results["sentiment"]["sentiment_score"],
            stress_level=results["behavioral_scores"]["stress_level"],
            confidence_level=results["behavioral_scores"]["confidence_level"],
            coherence_score=results["behavioral_scores"]["coherence_score"],
            pitch_mean=results["acoustic_features"]["pitch_mean"],
            speech_rate=results["acoustic_features"]["speech_rate"],
            pause_count=results["acoustic_features"]["pause_count"],
            energy_level=results["acoustic_features"]["energy_level"],
            processing_time_seconds=time.time() - start
        ))

        # 🔥 INSERTION QDRANT (CE QUI MANQUAIT)
        _qdrant.insert_audio_vector(
            audio_id=audio.id,
            vector=results["embedding"],
            metadata={
                "language": results["transcription"]["language"],
                "sentiment": results["sentiment"]["sentiment_score"],
                "stress": results["behavioral_scores"]["stress_level"],
                "confidence": results["behavioral_scores"]["confidence_level"],
                "created_at": datetime.utcnow().isoformat()
            }
        )

        audio.status = AudioStatus.COMPLETED
        audio.processing_completed_at = datetime.utcnow()
        audio.qdrant_point_id = f"audio_{audio.id}"

        db.commit()
        return {"status": "success", "audio_id": audio.id}

    except Exception as e:
        db.rollback()
        audio.status = AudioStatus.FAILED
        db.commit()
        raise e

    finally:
        db.close()

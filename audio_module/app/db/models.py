# Définit les modèles de données (ORM) pour le module audio.
"""
Modèles de base de données pour le module audio
Source unique : WhatsApp Business
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class AudioStatus(enum.Enum):
    """Statuts possibles d'un audio"""
    UPLOADED = "uploaded"           # Fichier reçu de WhatsApp
    PROCESSING = "processing"       # En cours de traitement
    COMPLETED = "completed"         # Traitement terminé
    FAILED = "failed"              # Erreur de traitement


class Audio(Base):
    """
    Table principale : fichiers audio reçus via WhatsApp Business
    """
    __tablename__ = "audios"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    format = Column(String(10), nullable=False)  # ogg, mp3, m4a (formats WhatsApp)
    file_path = Column(String(500), nullable=False)  # chemin dans audio_storage/
    duration_seconds = Column(Float, nullable=True)  # durée en secondes
    file_size_bytes = Column(Integer, nullable=True)
    
    # Métadonnées WhatsApp
    whatsapp_message_id = Column(String(100), nullable=True)  # ID du message WhatsApp
    whatsapp_phone_number = Column(String(20), nullable=True)  # Numéro du client (anonymisé)
    whatsapp_profile_name = Column(String(100), nullable=True)  # Nom du profil
    
    # Traitement
    status = Column(Enum(AudioStatus), default=AudioStatus.UPLOADED, nullable=False)
    qdrant_point_id = Column(String(100), nullable=True)  # ID dans Qdrant
    
    # Timestamps
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    
    # Relations (CORRECTION: metadata → processing_info)
    transcription = relationship("Transcription", back_populates="audio", uselist=False)
    processing_info = relationship("ProcessingMetadata", back_populates="audio", uselist=False)

    def __repr__(self):
        return f"<Audio(id={self.id}, filename='{self.filename}', status='{self.status.value}')>"


class Transcription(Base):
    """
    Table : transcriptions des audios WhatsApp
    """
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audios.id"), nullable=False)
    
    # Contenu
    text = Column(Text, nullable=False)
    language = Column(String(10), nullable=True)  # fr, ar, en (détecté par Whisper)
    confidence = Column(Float, nullable=True)  # score de confiance Whisper (0-1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relations
    audio = relationship("Audio", back_populates="transcription")

    def __repr__(self):
        return f"<Transcription(id={self.id}, audio_id={self.audio_id}, language='{self.language}')>"


class ProcessingMetadata(Base):
    """
    Table : métadonnées du traitement et analyses comportementales
    """
    __tablename__ = "processing_metadata"

    id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audios.id"), nullable=False)
    
    # Analyses comportementales
    sentiment_score = Column(Float, nullable=True)  # -1 (négatif) à +1 (positif)
    stress_level = Column(Float, nullable=True)  # 0 (calme) à 1 (très stressé)
    confidence_level = Column(Float, nullable=True)  # 0 (hésitant) à 1 (confiant)
    coherence_score = Column(Float, nullable=True)  # 0 (incohérent) à 1 (cohérent)
    
    # Features acoustiques (moyennes)
    pitch_mean = Column(Float, nullable=True)  # fréquence fondamentale moyenne (Hz)
    speech_rate = Column(Float, nullable=True)  # mots par minute
    pause_rate = Column(Float, nullable=True)  # ratio silence/durée
    energy_db = Column(Float, nullable=True)  # énergie vocale en dB
    
    # Scoring final (calculé avec Qdrant)
    solvability_score = Column(Float, nullable=True)  # 0 à 100
    similar_profiles_count = Column(Integer, nullable=True)  # nombre de profils similaires trouvés
    risk_indicators = Column(Text, nullable=True)  # JSON string avec red flags détectés
    
    # Performance
    processing_time_seconds = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relations (CORRECTION: back_populates="metadata" → back_populates="processing_info")
    audio = relationship("Audio", back_populates="processing_info")

    def __repr__(self):
        return f"<ProcessingMetadata(id={self.id}, audio_id={self.audio_id}, sentiment={self.sentiment_score})>"
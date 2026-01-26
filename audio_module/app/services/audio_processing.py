# Contient la logique métier pour le traitement des fichiers audio (conversion, analyse, etc.).
"""
Service de traitement et analyse des fichiers audio
"""
import whisper
import librosa
import numpy as np
from pathlib import Path
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from typing import Dict, Tuple, List


class AudioProcessor:
    """
    Classe pour le traitement complet des audios
    """
    
    def __init__(self):
        """
        Initialise les modèles (chargés une seule fois)
        """
        print("🔄 Chargement des modèles d'IA...")
        
        # Whisper pour transcription (modèle 'base' = bon compromis vitesse/qualité)
        # Options : tiny, base, small, medium, large
        self.whisper_model = whisper.load_model("base")
        
        # Sentiment analysis (français supporté)
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )
        
        # Génération embeddings pour Qdrant
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        print("✅ Modèles chargés avec succès")
    
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        Transcrit un fichier audio en texte avec Whisper
        
        Args:
            audio_path: Chemin vers le fichier audio
        
        Returns:
            dict avec texte, langue, confiance
        """
        print(f"🎤 Transcription de {audio_path}...")
        
        result = self.whisper_model.transcribe(
            audio_path,
            language=None,  # Détection automatique
            fp16=False  # Pas de GPU
        )
        
        return {
            "text": result["text"].strip(),
            "language": result["language"],
            "segments": result.get("segments", [])
        }
    
    
    def extract_acoustic_features(self, audio_path: str) -> Dict:
        """
        Extrait les features acoustiques (ton, rythme, énergie)
        
        Args:
            audio_path: Chemin vers le fichier audio
        
        Returns:
            dict avec pitch, speech_rate, pauses, energy
        """
        print(f"🔊 Extraction features acoustiques...")
        
        # Charger l'audio
        y, sr = librosa.load(audio_path, sr=16000)
        
        # 1. Pitch (fréquence fondamentale)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        pitch_mean = float(np.mean(pitch_values)) if pitch_values else 0.0
        pitch_std = float(np.std(pitch_values)) if pitch_values else 0.0
        
        # 2. Énergie vocale (RMS)
        rms = librosa.feature.rms(y=y)[0]
        energy_mean = float(np.mean(rms))
        energy_std = float(np.std(rms))
        
        # 3. Taux de parole approximatif (via onset detection)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        
        # 4. Détection de pauses (segments silencieux)
        intervals = librosa.effects.split(y, top_db=20)
        pause_count = len(intervals) - 1 if len(intervals) > 1 else 0
        
        return {
            "pitch_mean": pitch_mean,
            "pitch_variance": pitch_std ** 2,
            "speech_rate": float(tempo),
            "pause_count": pause_count,
            "energy_level": energy_mean
        }
    
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyse le sentiment du texte transcrit
        
        Args:
            text: Texte transcrit
        
        Returns:
            dict avec sentiment_score (-1 à +1) et label
        """
        print(f"💭 Analyse de sentiment...")
        
        if not text or len(text.strip()) < 5:
            return {
                "sentiment_score": 0.0,
                "label": "neutral",
                "confidence": 0.0
            }
        
        # Le modèle retourne 1-5 étoiles
        result = self.sentiment_analyzer(text[:512])[0]  # Limite 512 chars
        
        # Convertir 1-5 étoiles en score -1 à +1
        stars = int(result['label'].split()[0])
        sentiment_score = (stars - 3) / 2  # 1→-1, 2→-0.5, 3→0, 4→0.5, 5→1
        
        return {
            "sentiment_score": sentiment_score,
            "label": result['label'],
            "confidence": result['score']
        }
    
    
    def calculate_behavioral_scores(
        self,
        transcription: Dict,
        acoustic_features: Dict,
        sentiment: Dict
    ) -> Dict:
        """
        Calcule les scores comportementaux (stress, confiance, cohérence)
        
        Args:
            transcription: Résultat de transcription
            acoustic_features: Features acoustiques
            sentiment: Analyse de sentiment
        
        Returns:
            dict avec stress_level, confidence_level, coherence_score
        """
        print(f"📊 Calcul des scores comportementaux...")
        
        # 1. Niveau de stress (basé sur pitch variance + énergie)
        pitch_var_normalized = min(acoustic_features['pitch_variance'] / 10000, 1.0)
        energy_normalized = min(acoustic_features['energy_level'] / 0.1, 1.0)
        stress_level = (pitch_var_normalized * 0.6 + energy_normalized * 0.4)
        
        # 2. Niveau de confiance (basé sur sentiment + pauses)
        pause_penalty = min(acoustic_features['pause_count'] / 20, 0.3)
        sentiment_contribution = (sentiment['sentiment_score'] + 1) / 2  # 0 à 1
        confidence_level = max(0.0, sentiment_contribution - pause_penalty)
        
        # 3. Score de cohérence (basé sur longueur texte + nombre de segments)
        text_length = len(transcription['text'].split())
        segment_count = len(transcription.get('segments', []))
        coherence = min(text_length / 50, 1.0) * (1 - min(segment_count / 20, 0.5))
        
        return {
            "stress_level": float(stress_level),
            "confidence_level": float(confidence_level),
            "coherence_score": float(coherence)
        }
    
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Génère un vecteur d'embedding pour Qdrant
        
        Args:
            text: Texte transcrit
        
        Returns:
            Liste de floats (384 dimensions)
        """
        print(f"🧮 Génération de l'embedding vectoriel...")
        
        if not text or len(text.strip()) < 5:
            # Retourner un vecteur zéro si pas de texte
            return [0.0] * 384
        
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    
    def process_complete(self, audio_path: str) -> Dict:
        """
        Pipeline complet de traitement d'un audio
        
        Args:
            audio_path: Chemin vers le fichier audio
        
        Returns:
            dict avec tous les résultats
        """
        print(f"\n{'='*60}")
        print(f"🚀 DÉBUT TRAITEMENT COMPLET : {audio_path}")
        print(f"{'='*60}\n")
        
        # 1. Transcription
        transcription = self.transcribe_audio(audio_path)
        
        # 2. Features acoustiques
        acoustic_features = self.extract_acoustic_features(audio_path)
        
        # 3. Analyse sentiment
        sentiment = self.analyze_sentiment(transcription['text'])
        
        # 4. Scores comportementaux
        behavioral_scores = self.calculate_behavioral_scores(
            transcription,
            acoustic_features,
            sentiment
        )
        
        # 5. Génération embedding
        embedding = self.generate_embedding(transcription['text'])
        
        print(f"\n{'='*60}")
        print(f"✅ TRAITEMENT TERMINÉ")
        print(f"{'='*60}\n")
        
        return {
            "transcription": transcription,
            "acoustic_features": acoustic_features,
            "sentiment": sentiment,
            "behavioral_scores": behavioral_scores,
            "embedding": embedding
        }


# Instance globale (chargée une seule fois au démarrage du worker)
_audio_processor = None

def get_audio_processor() -> AudioProcessor:
    """
    Retourne l'instance singleton de AudioProcessor
    """
    global _audio_processor
    if _audio_processor is None:
        _audio_processor = AudioProcessor()
    return _audio_processor
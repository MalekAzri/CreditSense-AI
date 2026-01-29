# Contient la logique métier pour le traitement des fichiers audio (conversion, analyse, etc.).
"""
Service de traitement et analyse des fichiers audio
"""
import whisper
import librosa
import numpy as np
import subprocess
import os
import uuid
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

    def _empty_features(self):
        return {
            "pitch_mean": 0.0, "pitch_cv": 0.0, 
            "speech_rate": 0.0, "pause_rate": 0.0, 
            "energy_db": -80.0
        }

    
    
    
    
    def _load_audio_robust(self, audio_path: str, sr: int = 16000) -> Tuple[np.ndarray, int]:
        """
        Charge un fichier audio de manière robuste en le convertissant d'abord en WAV avec ffmpeg.
        Contourne les problèmes de codec (audioread) sur Windows pour les fichiers .m4a/.ogg.
        """
        path_obj = Path(audio_path)
        temp_wav = path_obj.parent / f"temp_{uuid.uuid4()}.wav"
        
        try:
            # Conversion forcée en WAV via ffmpeg
            # -y : overwrite
            # -vn : disable video
            # -ac 1 : mono (suffisant pour l'analyse)
            # -ar {sr} : sample rate
            command = [
                "ffmpeg", "-y", 
                "-i", str(audio_path),
                "-vn", 
                "-ac", "1", 
                "-ar", str(sr),
                str(temp_wav)
            ]
            
            # Exécuter ffmpeg silencieusement
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Charger le WAV propre avec librosa (utilise soundfile nativement)
            y, s = librosa.load(str(temp_wav), sr=sr)
            return y, s
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur FFmpeg : {e}")
            raise
        except Exception as e:
            print(f"❌ Erreur chargement robuste : {e}")
            # Fallback (non recommandé si m4a bug déjà)
            return librosa.load(audio_path, sr=sr)
        finally:
            # Nettoyage
            if temp_wav.exists():
                try:
                    os.remove(temp_wav)
                except:
                    pass

    
    def extract_acoustic_features(self, audio_path: str) -> Dict:
        """
        Extrait les features acoustiques (ton, rythme, énergie)
        
        Args:
            audio_path: Chemin vers le fichier audio
        
        Returns:
            dict avec pitch, speech_rate, pauses, energy (dB)
        """
        print(f"🔊 Extraction features acoustiques...")
        
        # Charger l'audio
        try:
            # Utilisation de la méthode robuste (ffmpeg -> wav -> librosa)
            y, sr = self._load_audio_robust(audio_path, sr=16000)
            
            print(f"   [DEBUG] Audio Loaded: duration={len(y)/sr:.2f}s, samples={len(y)}, checksum={np.sum(np.abs(y)):.2f}")
            if len(y) == 0:
                print("   ❌ ERREUR: Audio vide !")
                return self._empty_features()
        except Exception as e:
            print(f"   ❌ ERREUR CHARGEMENT LIBROSA/FFMPEG: {e}")
            return self._empty_features()
        
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
        # Coefficient de variation (plus robuste que variance brute)
        pitch_cv = (pitch_std / pitch_mean) if pitch_mean > 0 else 0.0
        
        # 2. Énergie vocale (dB)
        rms = librosa.feature.rms(y=y)[0]
        energy_mean_raw = float(np.mean(rms))
        # Convertir en décibels pour une échelle plus naturelle (logarithmique)
        # On ajoute 1e-6 pour éviter log(0)
        energy_db = 10 * np.log10(energy_mean_raw + 1e-6)
        
        # 3. Taux de parole approximatif (via onset detection)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        
        # 4. Détection de pauses (segments silencieux)
        intervals = librosa.effects.split(y, top_db=20)
        # Ratio de pauses par rapport à la durée totale
        duration = librosa.get_duration(y=y, sr=sr)
        pause_count = len(intervals) - 1 if len(intervals) > 1 else 0
        pause_rate = pause_count / duration if duration > 0 else 0
        
        return {
            "pitch_mean": pitch_mean,
            "pitch_cv": pitch_cv,  # Remplacé variance par CV
            "speech_rate": float(tempo),
            "pause_rate": float(pause_rate),
            "energy_db": energy_db
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
        
        if not text or len(text.strip()) < 2:
            return {
                "sentiment_score": 0.0,
                "label": "neutral",
                "confidence": 0.0
            }
        
        # Le modèle retourne 1-5 étoiles
        result = self.sentiment_analyzer(text[:512])[0]  # Limite 512 chars
        
        # Convertir 1-5 étoiles en score -1 à +1
        stars = int(result['label'].split()[0])
        sentiment_score = (stars - 3) / 2.0  # Force float division
        
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
        Calcule les scores comportementaux avec une logique améliorée
        
        Args:
            transcription: Résultat de transcription
            acoustic_features: Features acoustiques
            sentiment: Analyse de sentiment
        
        Returns:
            dict avec stress_level, confidence_level, coherence_score
        """
        print(f"📊 Calcul des scores comportementaux (V2)...")
        
        import math
        
        def sigmoid(x):
            return 1 / (1 + math.exp(-x))
        
        # 1. Niveau de stress
        # - Pitch CV élevé = instabilité (stress)
        # - Speech rate élevé = précipitation (stress)
        # - Énergie dB élevée = voix forte (colère/stress)
        
        # Normalisation dynamique heuristique
        norm_pitch = min(acoustic_features.get('pitch_cv', 0) * 2.0, 1.0) # CV ~0.2-0.5 normal
        norm_rate = min(acoustic_features['speech_rate'] / 200, 1.0) # 200 BPM max
        
        # Énergie : mapping de -40dB (calme) à -10dB (fort) vers 0-1
        energy_db = acoustic_features.get('energy_db', -30)
        norm_energy = max(0.0, min((energy_db + 40) / 30, 1.0))
        
        # Formule pondérée
        raw_stress = (norm_pitch * 0.3) + (norm_rate * 0.2) + (norm_energy * 0.5)
        # Lissage sigmoid pour "pousser" les valeurs vers les extrêmes si significatives
        stress_level = sigmoid((raw_stress - 0.5) * 5) # Centré sur 0.5
        
        # 2. Niveau de confiance (Approche Risque Crédit)
        # - Confiance augmente si le client est calme (Stress Faible)
        # - Confiance augmente si le sentiment est positif
        # - Confiance diminue si le client crie ou est instable (Stress Élevé)
        
        pause_penalty = min(acoustic_features.get('pause_rate', 0) * 2.0, 0.5)
        
        # Sentiment (-1 à 1) -> (0 à 1)
        sentiment_val = (sentiment['sentiment_score'] + 1) / 2
        
        # Le Stress impacte NÉGATIVEMENT la confiance dans un contexte bancaire
        # (contrairement à l'analyse de sentiment classique où colère = confiance en soi)
        stress_penalty = float(stress_level) * 0.5  # Pénalité forte
        
        # Confiance = (Sentiment * 40%) + (Calme * 40%) - (Pauses * 20%)
        # Calme = 1 - stress_level
        raw_confidence = (sentiment_val * 0.4) + ((1.0 - float(stress_level)) * 0.4) + ((1.0 - pause_penalty) * 0.2)
        
        confidence_level = max(0.0, min(raw_confidence, 1.0))
        
        # 3. Score de cohérence
        text_length = len(transcription['text'].split())
        segment_count = len(transcription.get('segments', []))
        
        # Ratio segments/mots : peu de mots par segment = haché
        density = text_length / (segment_count + 1)
        norm_density = min(density / 10, 1.0) # 10 mots par segment = bien
        
        coherence = norm_density * min(text_length / 20, 1.0)
        
        return {
            "stress_level": round(float(stress_level), 2),
            "confidence_level": round(float(confidence_level), 2),
            "coherence_score": round(float(coherence), 2)
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
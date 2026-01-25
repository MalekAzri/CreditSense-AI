"""
Module CLIP: Génération d'embeddings d'images et calcul de similarité.
"""

import sys
import torch
import numpy as np
from transformers import CLIPProcessor, CLIPModel

from .utils import load_image
from .config import CLIP_MODEL_ID, MODELS_LOCAL_FILES_ONLY

# =========================
# CACHE GLOBAL
# =========================
_clip_model = None
_clip_processor = None


def get_clip_model():
    """
    Charge le modèle CLIP et le processor UNE SEULE FOIS
    """
    global _clip_model, _clip_processor

    if _clip_model is None or _clip_processor is None:
        print(
            f"[CACHE] Chargement du modèle CLIP "
            f"{CLIP_MODEL_ID} (local_only={MODELS_LOCAL_FILES_ONLY})"
        )

        _clip_model = CLIPModel.from_pretrained(
            CLIP_MODEL_ID,
            local_files_only=MODELS_LOCAL_FILES_ONLY,
        )
        _clip_model.eval()

        _clip_processor = CLIPProcessor.from_pretrained(
            CLIP_MODEL_ID,
            local_files_only=MODELS_LOCAL_FILES_ONLY,
        )

    return _clip_model, _clip_processor


def generate_clip_vector(image_path: str):
    try:
        model, processor = get_clip_model()

        image = load_image(image_path)
        inputs = processor(images=image, return_tensors="pt")

        with torch.no_grad():
            features = model.get_image_features(**inputs)

        features = features / features.norm(p=2, dim=-1, keepdim=True)

        return features.cpu().numpy().flatten()

    except Exception as e:
        print(f"Erreur CLIP: {e}", file=sys.stderr)
        return None


def compute_similarity(vector1, vector2):
    try:
        if isinstance(vector1, torch.Tensor):
            vector1 = vector1.cpu().numpy()
        if isinstance(vector2, torch.Tensor):
            vector2 = vector2.cpu().numpy()

        vector1 = vector1.flatten()
        vector2 = vector2.flatten()

        denom = np.linalg.norm(vector1) * np.linalg.norm(vector2)
        if denom == 0:
            return 0.0

        return float(np.dot(vector1, vector2) / denom)

    except Exception as e:
        print(f"Erreur similarité: {e}", file=sys.stderr)
        return 0.0

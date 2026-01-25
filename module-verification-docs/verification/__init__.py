"""
Package d'initialisation pour le module de vérification de documents.
"""
from . import env_setup
from .ocr import extract_text_from_image, generate_text_embedding
from .clip import generate_clip_vector, compute_similarity
from .verify_document import verify_document, store_reference_vector

__all__ = [
    'extract_text_from_image',
    'generate_text_embedding',
    'generate_clip_vector',
    'compute_similarity',
    'verify_document',
    'store_reference_vector'
]

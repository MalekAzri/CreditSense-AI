"""
Utilitaires partagés pour le traitement d'images.
"""

import os
from PIL import Image, ImageOps
import sys

def load_image(image_path: str) -> Image.Image:
    """
    Charge une image depuis un chemin de fichier.
    
    Args:
        image_path (str): Chemin vers le fichier image
        
    Returns:
        PIL.Image.Image: Image chargée
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        Exception: Si l'image ne peut pas être chargée
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Le fichier image n'existe pas: {image_path}")
    
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        raise Exception(f"Erreur lors du chargement de l'image: {e}")

def preprocess_image_for_ocr(image: Image.Image, upscale_factor: int = 3) -> Image.Image:
    """
    Prétraite une image pour améliorer la qualité de l'OCR.
    
    Args:
        image (PIL.Image.Image): Image à prétraiter
        upscale_factor (int): Facteur d'agrandissement (défaut: 3)
        
    Returns:
        PIL.Image.Image: Image prétraitée
    """
    try:
        # Upscaling pour aider Tesseract à mieux voir les lettres
        processed_image = image.resize(
            (image.width * upscale_factor, image.height * upscale_factor),
            Image.Resampling.BICUBIC
        )
        
        # Conversion en niveaux de gris
        processed_image = processed_image.convert("L")
        
        # Amélioration du contraste
        processed_image = ImageOps.autocontrast(processed_image)
        
        return processed_image
    except Exception as e:
        print(f"Erreur lors du prétraitement de l'image: {e}", file=sys.stderr)
        return image

def validate_image_path(image_path: str) -> bool:
    """
    Valide qu'un chemin d'image existe et est un fichier valide.
    
    Args:
        image_path (str): Chemin vers le fichier image
        
    Returns:
        bool: True si le chemin est valide, False sinon
    """
    if not os.path.exists(image_path):
        return False
    
    if not os.path.isfile(image_path):
        return False
    
    # Vérifier l'extension du fichier
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    _, ext = os.path.splitext(image_path)
    
    return ext.lower() in valid_extensions

def get_absolute_path(relative_path: str, base_dir: str = None) -> str:
    """
    Convertit un chemin relatif en chemin absolu.
    
    Args:
        relative_path (str): Chemin relatif
        base_dir (str): Répertoire de base (optionnel)
        
    Returns:
        str: Chemin absolu
    """
    if os.path.isabs(relative_path):
        return relative_path
    
    if base_dir is None:
        base_dir = os.getcwd()
    
    return os.path.abspath(os.path.join(base_dir, relative_path))

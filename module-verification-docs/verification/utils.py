"""
Utilitaires partagés pour le traitement d'images.
"""

import os
import cv2
import numpy as np
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
    Prétraite une image pour améliorer la qualité de l'OCR en utilisant OpenCV.
    
    Args:
        image (PIL.Image.Image): Image à prétraiter
        upscale_factor (int): Facteur d'agrandissement (défaut: 3)
        
    Returns:
        PIL.Image.Image: Image prétraitée
    """
    try:
        # Convertir PIL Image en tableau numpy (OpenCV)
        # S'assurer que l'image est en RGB avant la conversion si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        img_np = np.array(image)
        # Convertir de RGB à BGR (format standard OpenCV)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # 1. Upscaling (Redimensionnement)
        width = int(img_cv.shape[1] * upscale_factor)
        height = int(img_cv.shape[0] * upscale_factor)
        img_cv = cv2.resize(img_cv, (width, height), interpolation=cv2.INTER_CUBIC)

        # 2. Passage en niveaux de gris
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 3. Réduction du bruit (Denoising)
        # h=10 est un bon point de départ pour le filtrage
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # 4. Seuillage adaptatif (Adaptive Thresholding)
        # Utile pour les documents avec un éclairage inégal
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )

        # Reconvertir en PIL Image pour la compatibilité avec le reste du code
        processed_image = Image.fromarray(thresh)
        
        return processed_image
    except Exception as e:
        print(f"Erreur lors du prétraitement OpenCV: {e}", file=sys.stderr)
        # Fallback sur la méthode PIL simple en cas d'erreur
        try:
            processed_image = image.resize(
                (image.width * upscale_factor, image.height * upscale_factor),
                Image.Resampling.BICUBIC
            ).convert("L")
            return ImageOps.autocontrast(processed_image)
        except:
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

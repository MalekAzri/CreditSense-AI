"""
Configuration initiale de l'environnement pour forcer l'utilisation du disque D:.
Ce module DOIT être importé en premier.
"""
import os

# ========== CONFIGURATION DES CHEMINS SUR D: ==========
D_ROOT = r"D:\CreditSense Ai"
HF_CACHE_DIR = os.path.join(D_ROOT, "huggingface_cache")
TORCH_CACHE = os.path.join(D_ROOT, "torch_cache")
TMP_DIR = os.path.join(D_ROOT, "temp")

# Créer les dossiers
for path in [HF_CACHE_DIR, TORCH_CACHE, TMP_DIR]:
    os.makedirs(path, exist_ok=True)

# ========== VARIABLES D'ENVIRONNEMENT HUGGING FACE ==========
os.environ['HF_HOME'] = HF_CACHE_DIR
os.environ['HF_HUB_CACHE'] = os.path.join(HF_CACHE_DIR, "hub")
os.environ['HF_DATASETS_CACHE'] = os.path.join(HF_CACHE_DIR, "datasets")
os.environ['TRANSFORMERS_CACHE'] = os.path.join(HF_CACHE_DIR, "transformers")
os.environ['SENTENCE_TRANSFORMERS_HOME'] = os.path.join(HF_CACHE_DIR, "sentence_transformers")
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

# ========== VARIABLES D'ENVIRONNEMENT TORCH & TEMP ==========
os.environ['TORCH_HOME'] = TORCH_CACHE
os.environ['TEMP'] = TMP_DIR
os.environ['TMP'] = TMP_DIR
os.environ['TMPDIR'] = TMP_DIR
os.environ['PYTHON_EGG_CACHE'] = os.path.join(TMP_DIR, "eggs")

print(f"Environnement initialisé sur {D_ROOT}")

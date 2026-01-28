# Module de Verification de Documents - CreditSense AI

## Description

Systeme modulaire de verification de documents utilisant l'IA pour authentifier des documents d'identite (CIN, passeports, etc.) via:
- **CLIP** pour les embeddings d'images
- **OCR + Sentence Transformers** pour les embeddings de texte
- **Qdrant** pour le stockage et la comparaison de vecteurs de reference

## Architecture

```
module-verification-docs/
├── verification/
│   ├── __init__.py          # Exports du package
│   ├── config.py            # Configuration centralisee
│   ├── utils.py             # Utilitaires partager
│   ├── ocr.py               # Extraction texte + embeddings
│   ├── clip.py              # Embeddings d'images
│   └── verify_document.py   # Orchestrateur + Qdrant
├── docs/                    # Documents de test
├── main.py                  # Point d'entree principal
└── requirements.txt         # Dependances Python
```

## Installation

### 1. Installer les dependances Python

```bash
pip install -r requirements.txt
```

### 2. Installer Tesseract OCR

**Windows:**
- Telecharger depuis: https://github.com/UB-Mannheim/tesseract/wiki
- Ajouter au PATH systeme

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-ara
```

### 3. Installer et demarrer Qdrant

**Option 1: Qdrant Cloud (recommande pour la production)**

Consultez le guide detaille : [QDRANT_CLOUD_SETUP.md](QDRANT_CLOUD_SETUP.md)

1. Creez un cluster sur https://cloud.qdrant.io/
2. Recuperez l'URL et l'API Key
3. Configurez dans `verification/config.py` :
   ```python
   QDRANT_USE_CLOUD = True
   QDRANT_CLOUD_URL = "https://votre-cluster.eu-central.aws.cloud.qdrant.io:6333"
   QDRANT_CLOUD_API_KEY = "votre-api-key"
   ```

**Option 2: Docker (pour developpement local)**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Option 3: Installation locale**
Suivre les instructions sur: https://qdrant.tech/documentation/quick-start/

## Utilisation

### Mode interactif

```bash
python main.py
```

Le script propose 3 modes:
1. **Stocker un vecteur de reference legitime** - Pour enregistrer des documents authentiques
2. **Verifier un document** - Pour valider un document contre les references
3. **Test complet** - Stockage puis verification

### Utilisation programmatique

```python
from verification import verify_document, store_reference_vector
from verification.clip import generate_clip_vector
from verification.ocr import extract_and_embed

# Stocker une reference legitime
clip_vector = generate_clip_vector("docs/CIN_legitime.png")
store_reference_vector(
    document_type="CIN",
    vector_type="clip",
    vector=clip_vector,
    point_id=1,
    metadata={"source": "CIN_reference_1"}
)

# Verifier un document
result = verify_document("docs/CIN_a_verifier.png", document_type="CIN")

if result["is_valid"]:
    print("[OK] Document authentique")
else:
    print("[SUSPECT] Document suspect")
```

## Configuration

Modifier `verification/config.py` pour ajuster:

- **Seuils de similarite** (`SIMILARITY_THRESHOLDS`)
- **Connexion Qdrant** (`QDRANT_HOST`, `QDRANT_PORT`)
- **Modeles utilises** (`CLIP_MODEL_ID`, `TEXT_EMBEDDING_MODEL_ID`)
- **Cache des modeles** (`HF_CACHE_DIR`)

## Fonctionnement

### 1. Stockage des references

Pour chaque document legitime:
1. Generation d'un vecteur CLIP (image)
2. Extraction du texte via OCR
3. Generation d'un vecteur textuel (Sentence Transformer)
4. Stockage dans Qdrant avec metadonnees

### 2. Verification d'un document

Pour un document a verifier:
1. Generation des vecteurs CLIP et OCR
2. Recherche des vecteurs les plus similaires dans Qdrant
3. Calcul de la similarite cosinus
4. Validation si les scores depassent les seuils configures

### 3. Resultat

```json
{
  "is_valid": true,
  "clip_similarity": 0.92,
  "ocr_similarity": 0.87,
  "clip_threshold": 0.85,
  "ocr_threshold": 0.75,
  "extracted_text": "...",
  "clip_match": {...},
  "ocr_match": {...}
}
```

## Avantages de cette architecture

- **Pas de duplication de code** - Logique partagee dans des modules reutilisables  
- **Scalable** - Ajout facile de nouveaux types de documents  
- **Maintenable** - Chaque module a une responsabilite unique  
- **Testable** - Modules independants faciles a tester  
- **Flexible** - Configuration centralisee et personnalisable  

## Ajouter un nouveau type de document

1. Ajouter la configuration dans `verification/config.py`:

```python
QDRANT_COLLECTIONS["PASSPORT"] = {
    "clip_collection": "passport_clip_vectors",
    "ocr_collection": "passport_ocr_vectors",
    "vector_size_clip": 512,
    "vector_size_ocr": 384,
}

SIMILARITY_THRESHOLDS["PASSPORT"] = {
    "clip_threshold": 0.80,
    "ocr_threshold": 0.70,
}
```

2. Utiliser avec `document_type="PASSPORT"`:

```python
verify_document("docs/passport.png", document_type="PASSPORT")
```

## Depannage

### Erreur "No space left on device"
- Le cache des modeles est configure sur `D:\CreditSense Ai\huggingface_cache`
- Modifier `HF_CACHE_DIR` dans `config.py` si necessaire

### Erreur de connexion Qdrant
- Verifier que Qdrant est demarre: `docker ps` ou verifier le service local
- Verifier `QDRANT_HOST` et `QDRANT_PORT` dans `config.py`

### OCR ne detecte pas le texte arabe
- Verifier que Tesseract est installe avec le support arabe
- Tester: `tesseract --list-langs` (doit afficher "ara")

## Licence

CreditSense AI - Module de verification de documents

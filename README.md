# CreditSense AI

CreditSense AI est une plateforme intelligente d'analyse de prêts et d'aide à la prise de décision destinée aux analystes financiers.
Elle permet de centraliser les demandes de crédit, d'évaluer les risques, de détecter la fraude documentaire, d'analyser les messages textuels et vocaux, et de fournir des recommandations explicables basées sur l'intelligence artificielle.

---

## Vision Générale

La plateforme vise à assister les analystes dans :

* l'évaluation du risque crédit,
* la détection de fraudes (documents, messages, comportements),
* la centralisation des données multi-sources (documents, emails, WhatsApp, audio),
* la justification claire des décisions prises par l'IA.

---

## Structure du Projet

### 1. Frontend (version synthétique)

Le frontend présente une vision globale de la plateforme CreditSense AI.

Fonctionnalités principales :

* Dashboard de suivi des prêts :

  * état du prêt,
  * alertes de risque,
  * décisions prises par les analystes.
* Page d'analyse détaillée (au clic sur un prêt) :

  * pourcentage de risque,
  * recommandation IA (accorder ou refuser le crédit),
  * justification de la décision (pourquoi oui / pourquoi non),
  * documents détectés comme fraudés avec leurs pourcentages de crédibilité.
* Section paramètres :

  * intégration d'APIs externes (emails, plateformes bancaires, etc.).
* Authentification des analystes (login sécurisé).

---

### 2. Module de Vérification de Documents (module-verification-docs)

Ce module permet de vérifier l'authenticité des documents d'identité tels que les cartes CIN et les passeports.

Fonctionnement :

* Les documents de référence sont transformés en vecteurs et stockés dans Qdrant.
* Les modèles OCR, CLIP et Sentence Transformers sont utilisés pour :

  * extraire le texte des documents,
  * analyser le contenu visuel,
  * convertir images et textes en représentations vectorielles.
* Lorsqu'un nouveau document est soumis, il est comparé aux vecteurs de référence afin de mesurer la similarité et détecter les fraudes ou incohérences.

Fonctionnalités :

* Détection du type de document (CIN, passeport, etc.).
* Analyse visuelle et textuelle.
* Score de similarité et crédibilité du document.
* Interface de test via menu déroulant.

---

### 3. Module de Calcul de Risque (Credit Scoring)

Ce module utilise le Machine Learning pour prédire la capacité d'un client à rembourser un prêt.

#### Présentation

Il s'appuie sur le jeu de données German Credit afin d'entraîner des modèles capables de classer une demande de crédit en deux catégories :

* Accordé
* Refusé

#### Critères de décision analysés

* Situation financière :

  * état du compte courant,
  * épargne,
  * montant du crédit.
* Profil personnel :

  * âge,
  * emploi,
  * statut marital,
  * situation de logement.
* Historique de crédit :

  * comportement de remboursement,
  * nombre de crédits existants.
* Conditions du prêt :

  * durée,
  * objectif du crédit (auto, immobilier, éducation, etc.).

#### Installation

```bash
pip install pandas numpy scikit-learn
```

#### Utilisation

1. Chargement des données :

```bash
python src/load_data.py
```

2. Entraînement du modèle :

```bash
python src/credit_scoring.py
```

Le meilleur modèle est automatiquement sauvegardé dans le dossier `models/`.

3. Test sur un nouveau client :

```bash
python src/test_new_client.py
```

#### Structure du module

* `src/` : scripts de traitement et d'entraînement
* `data/` : données brutes et transformées
* `models/` : modèle final sauvegardé

Technologies utilisées :

* Python
* Pandas
* NumPy
* Scikit-learn (Random Forest, Régression Logistique)

---

### 4. Module de Vérification de Textes et Emails (NLP)

Ce module analyse les messages textuels (emails, WhatsApp, etc.) liés aux demandes de crédit afin d'en extraire les informations clés et de comprendre le contexte.

Fonctionnalités :

* Nettoyage avancé des messages (suppression du bruit, signatures, HTML).
* Analyse sémantique pour comprendre l'intention du client.
* Extraction d'entités :

  * montants financiers,
  * noms,
  * CIN,
  * numéros de téléphone,
  * références de dossier.
* Centralisation des messages provenant de différentes sources.

#### Structure

* `app/` :

  * `main.py` : API FastAPI (messages, webhooks WhatsApp)
  * `models.py` : modèles Pydantic
* `scripts/` :

  * `process_messages.py` : moteur d'analyse NLP
  * `gmail_fetch.py`, `whatsapp_fetch.py`, `bank_fetch.py`
  * utilitaires de logging et de vérification MongoDB

#### Installation

Prérequis :

* Python 3.8+
* MongoDB
* Modèle spaCy français :

```bash
python -m spacy download fr_core_news_lg
```

Installation des dépendances :

```bash
pip install -r requirements.txt
```

Configuration via fichier `.env` :

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=creditapp
WHATSAPP_VERIFY_TOKEN=your_token
```

#### Utilisation

Lancer l'API :

```bash
uvicorn app.main:app --reload
```

Lancer le traitement NLP :

```bash
python scripts/process_messages.py
```

---

### 5. Module Audio (Analyse Comportementale)

Ce module traite et analyse les messages vocaux (notamment WhatsApp) afin d'extraire des indicateurs comportementaux utiles à l'analyse du risque.

Fonctionnalités :

* API REST basée sur FastAPI.
* Traitement asynchrone via Celery et Redis.
* Stockage des métadonnées avec SQLAlchemy.
* Analyse comportementale :

  * sentiment,
  * stress,
  * cohérence du discours,
  * indicateurs de solvabilité.

#### Installation

Prérequis :

* Python 3.8+
* Redis

Installation :

```bash
pip install -r requirements.txt
```

#### Démarrage

```bash
uvicorn app.main:app --reload
```

Documentation API :

* [http://localhost:8000/docs](http://localhost:8000/docs)

#### Endpoints principaux

* `POST /api/audio/upload`
* `GET /api/audio/status/{audio_id}`
* `GET /api/audio/results/{audio_id}`
* `GET /api/audio/list`

#### Structure

```
audio_module/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── services/
│   ├── workers/
│   └── main.py
├── audio_module.db
├── requirements.txt
└── README.md
```

---

## Fonctionnement Technique Détaillé des Modèles IA

### 1. Système de Réponses Automatiques (Auto-Reply)

Ce module utilise une approche hybride combinant Machine Learning classique et NLP moderne pour comprendre et répondre aux emails des clients.

#### 1. Machine Learning & NLP (Le Cerveau)
*   **Scikit-Learn (Random Forest)** : Utilisé pour la classification d'intention (déterminer si l'email est une "demande de document", "demande de statut", etc.).
*   **TF-IDF Vectorization** : Convertit le texte des emails en vecteurs numériques pour le modèle Random Forest.
*   **spaCy (`fr_core_news_lg`)** : Utilisé pour la Reconnaissance d'Entités Nommées (NER) afin d'extraire les noms des clients du corps de l'email.
*   **SentenceTransformers** : Génère des embeddings sémantiques pour la recherche de similarité (trouver des emails passés similaires).

#### 2. Traitement des Données & Extraction (Les Yeux)
*   **BeautifulSoup** : Nettoie le contenu HTML brut des emails pour obtenir du texte pur.
*   **Expressions Régulières (Regex)** : Largement utilisées pour extraire des motifs spécifiques comme :
    *   Numéros CIN (8 chiffres)
    *   Numéros de téléphone
    *   Montants financiers
    *   Adresses email
*   **Pandas** : Manipulation des données.

#### 3. Infrastructure & Stockage (La Mémoire)
*   **Qdrant** : Base de données vectorielle utilisée pour stocker et récupérer les embeddings d'emails pour la recherche de similarité sémantique.
*   **Joblib** : Utilisé pour sauvegarder et charger le modèle Random Forest entraîné et les templates de réponse.

#### 4. Intégration & Logique
*   **Python** : La logique backend.
*   **Next.js API** : Le système appelle votre API interne (`/api/webhook/client-lookup`) pour récupérer le statut du client en temps réel et les documents manquants.
*   **Templating Dynamique** : Utilise des f-strings Python pour injecter les données spécifiques au client (Nom, Statut, Documents Manquants) dans les templates de réponse prédéfinis.

#### 5. Fichiers Clés
*   **Modèles Entraînés** :
    *   `models/email_classifier.joblib` : Le classifieur Random Forest.
    *   `models/responses.joblib` : Les templates de réponse textuels.
*   **Backend Services** :
    *   `app/services/reply_generator.py` : Moteur de génération de réponse.
    *   `app/main.py` : Expose l'endpoint `/messages/generate-reply`.
*   **Frontend Integration** :
    *   `frontend/src/components/dashboard/EmailReplyModal.tsx` : Interface utilisateur appelant l'IA.

### 2. Système de Vérification de Documents (IA Hybride)

Ce module permet de valider l'authenticité des documents (CIN, Passeport) en comparant sémantiquement le document reçu avec des documents de référence validés.

#### Fonctionnement Technique et Usage de la Base Vectorielle (Qdrant)

L'originalité de ce module repose sur l'utilisation de **Vector Embeddings** pour la vérification, plutôt que de simples règles statiques.

**A. Phase d'Indexation (Les Références) :**
1.  Nous chargeons des images de documents valides (ex: une "vraie" CIN type).
2.  L'IA génère deux types de vecteurs pour chaque document :
    *   **Vecteur Visuel (CLIP)** : Une empreinte numérique représentant l'aspect visuel global (couleurs, disposition, logos).
    *   **Vecteur Textuel (OCR + SentenceTransformers)** : Une empreinte sémantique du texte extrait.
3.  Ces vecteurs de référence sont stockés dans **Qdrant** dans des collections distinctes (`cin_clip_collection`, `cin_ocr_collection`).

**B. Phase de Vérification (Le Test) :**
Lorsqu'un utilisateur soumet un document :
1.  Le système génère ses vecteurs (Visuel + Textuel).
2.  Il interroge **Qdrant** pour mesurer la distance (Cosine Similarity) avec les vecteurs de référence légitimes.
    *   *Si la similarité visuelle est > seuil (içi: 0.70) -> Le document ressemble visuellement à une CIN.
    *   *Si la similarité textuelle est > seuil(içi: 0.70) -> Le contenu textuel est cohérent avec une CIN.
3.  Le document n'est validé que si **les deux** scores dépassent les seuils de sécurité.

#### Technologies Clés
*   **Qdrant** : Le cœur du système. Stocke la "vérité terrain" sous forme de vecteurs.
*   **CLIP (OpenAI)** : Modèle multimodal comprenant la sémantique de l'image.
*   **Tesseract OCR** : Extraction brute du texte.
*   **SentenceTransformers** : Contextualisation du texte OCR (tolère les petites erreurs de lecture).

#### Fichiers Clés
*   `module-verification-docs/verification/verify_document.py` : Chef d'orchestre de la vérification. Interroge Qdrant.
*   `module-verification-docs/populate_qdrant.py` : Script critique pour générer et stocker les vecteurs de référence dans la base.
*   `module-verification-docs/verification/clip.py` : Génération des embeddings visuels.
*   `module-verification-docs/verification/ocr.py` : Pipeline OCR + Embedding textuel.

### 3. Module d'Analyse des Emails (NLP & Extraction)

Ce module, situé principalement sous `scripts/` et `app/services/`, est conçu pour transformer des emails non structurés en données structurées exploitables par le système bancaire.

#### Fonctionnement Technique

Le pipeline de traitement suit ces étapes rigoureuses :

1.  **Ingestion Multi-Source (Configuration Active)** :
    *   **Gmail (`banque.2026@gmail.com`)** : L'écoute est déjà opérationnelle grâce à l'authentification Cloud (OAuth2).
        *   **Scripts d'Auth** : L'accès sécurisé est géré via `scripts/credentials.json` (Client ID) et `scripts/token.json` (Token persistant).
        *   **Script de Récupération** : `scripts/gmail_fetch.py` se connecte automatiquement, télécharge les nouveaux emails non lus et les injecte dans le pipeline.
    *   **WhatsApp** : Géré via `scripts/whatsapp_fetch.py`.
    *   Le contenu est ensuite nettoyé (suppression HTML, signatures, disclaimers) via **BeautifulSoup**.

2.  **Analyse NLP Avancée (Spacy)** :
    *   Le texte nettoyé passe dans le pipeline `fr_core_news_lg`.
    *   **NER (Named Entity Recognition)** : Extraction automatique des Noms de personnes.
    *   **Détection d'Intention** : Analyse sémantique pour classifier le type de crédit demandé (Immobilier, Auto, Consommation) en comparant le texte avec des vecteurs de référence (via `doc.similarity`).

3.  **Extraction de Données (Regex & Heuristiques)** :
    *   Pour les données rigides, des **Regex** complexes sont utilisées :
        *   Montants (avec détection de devises et validateurs de contexte).
        *   CIN (8 chiffres, distinction avec numéros de téléphone).
        *   Numéros de téléphone (formats tunisiens).

4.  **Historique Sémantique (Qdrant)** :
    *   Chaque email entrant est vectorisé ("Embedding") par **SentenceTransformers**.
    *   Ce vecteur est stocké dans **Qdrant** (`synthetic_emails` collection).
    *   **Usage Clé** : Cela permet de retrouver des emails "similaires" passés pour :
        *   Détecter des doublons ou des relances.
        *   Aider le classifieur d'intention en regardant comment des emails similaires ont été traités.

#### Fichiers Clés (Scripts & Services)
*   `scripts/process_messages.py` : Script batch principal qui orchestre tout le pipeline NLP sur les nouveaux messages.
*   `app/services/email_processor.py` : Classe `EmailProcessor` contenant toute la logique métier (Nettoyage, NLP, Vectorisation).
*   `scripts/gmail_fetch.py` : Connecteur OAuth2 pour l'API Gmail.
*   `scripts/vectorize_emails.py` : Utilitaire pour régénérer les vecteurs Qdrant.

### 4. Module Audio (Analyse Comportementale)

Ce module traite les messages vocaux (notamment WhatsApp) pour extraire des signaux invisibles à l'écrit, en utilisant une architecture asynchrone pour la performance.

#### Fonctionnement Technique (Async Pipeline)

1.  **Ingestion & File d'Attente (FastAPI + Celery)** :
    *   L'audio est uploadé via l'API (`/api/audio/upload`).
    *   Une tâche est immédiatement placée dans une file d'attente **Redis** (Broker) via **Celery**. Cela garantit que l'API reste réactive même si l'analyse prend du temps.

2.  **Traitement Audio (Workers)** :
    *   Les **Workers Celery** (processus d'arrière-plan) récupèrent la tâche.
    *   **Transcodage** : Normalisation du fichier audio (conversions formats propriétaires vers WAV).
    *   **Extraction de Caractéristiques** : Analyse spectrale pour détecter :
        *   **Sentiment** : Tonalité positive/négative.
        *   **Stress** : Analyse des micro-tremblements (Jitter/Shimmer) et de la hauteur de voix (Pitch).
        *   **Indice de Cohérence** : Fluidité du discours (pauses, hésitations).

3.  **Stockage Persistant (SQLAlchemy)** :
    *   Les métadonnées et résultats d'analyse sont stockés dans `audio_module.db` via l'ORM **SQLAlchemy**, permettant un suivi historique de l'état émotionnel du client.

#### Fonctionnement Technique et Usage de Qdrant

Ce module ne se contente pas de transcrire l'audio, il le "vectorise" pour des comparaisons comportementales.

*   **Modèles IA Utilisés** :
    *   **Whisper (OpenAI)** : Utilisé pour la transcription Speech-to-Text robuste, gérant l'arabe dialectal et le français.
    *   **VADER / BERT Multilingual** : Analyse de sentiment sur le texte transcrit.
    *   **Librosa** (Traitement du signal) : Extraction des caractéristiques acoustiques brutes (Pitch, Jitter, Shimmer).

*   **Rôle de la Base Vectorielle (Qdrant)** :
    *   Nous construisons un **"Vecteur Comportemental"** composé des indicateurs clés : `[Score Sentiment, Niveau Stress, Débit de parole, Taux de pause]`.
    *   Ce vecteur est stocké dans Qdrant.
    *   **Logique de Scoring (K-NN)** : Pour chaque nouvel audio, le système récupère les **5 vecteurs les plus proches** dans la base. Le score final (ex: niveau de risque ou solvabilité) est obtenu en faisant la **moyenne des scores** (sentiment, stress) de ces 5 voisins historiques. Cela permet de prédire le comportement en se basant sur des précédents similaires.

#### Fichiers Clés
*   `audio_module/app/api/audio.py` : Endpoints API pour l'upload et la consultation des résultats.
*   `audio_module/app/workers/audio_worker.py` : Le consommateur Celery qui exécute l'analyse lourde.
*   `audio_module/app/services/audio_processing.py` : Logique scientifique de traitement du signal audio.
*   `audio_module/app/main.py` : Point d'entrée de l'application FastAPI dédiée.

---

## Sources de Données et Scalabilité

Chaque module s'appuie sur une stratégie de données spécifique pour garantir performance et évolutivité sans dépendre de datasets massifs propriétaires.

### 1. Module Scoring (Risque)
*   **Dataset** : `German Credit Dataset`. C'est un dataset standard académique utilisé pour entraîner le modèle Random Forest initial.
*   **Scalabilité** : Le modèle est léger (`pickle` < 10Mo). Pour passer à l'échelle, il suffit de réentraîner le modèle sur l'historique réel de la banque collecté au fil du temps (le script `train_model.py` est conçu pour être relancé périodiquement).

### 2. Module Vérification Documents
*   **Dataset** : **Pas de dataset d'entraînement classique**. Il utilise une approche **"Few-Shot Learning"**.
*   **Méthode** : Nous stockons uniquement quelques "Vecteurs de Référence" (ex: 1 image de CIN valide) dans Qdrant.
*   **Scalabilité (Semi-Supervisé)** : Pour ajouter un nouveau document, il suffit d'ajouter une seule image de référence. De plus, lorsqu'un document est validé manuellement comme "Légitime", il peut être ajouté à la base vectorielle. Cela crée une diversité de vecteurs qui **améliore la précision de l'analyse au fil du temps** (apprentissage continu).

### 3. Module Analyse Email
*   **Dataset** : Données Synthétiques (`scripts/generate_synthetic_data.py`). Nous générons des centaines de variantes d'emails types pour entraîner le classifieur.
*   **Scalabilité** : L'usage de Qdrant permet une "Mémoire Long Terme". Le système devient plus intelligent à chaque email traité car il peut se référer aux réponses passées  (RAG - Retrieval Augmented Generation).

### 4. Module Audio
*   **Dataset** : **Base de Référence Interne**. Comme pour les documents, nous avons généré nos propres audios de référence (simulation de voix stressées, confiantes, hésitantes) pour calibrer le système.
*   **Scalabilité** : Cette base s'enrichit naturellement avec le temps. Chaque nouvel audio traité et validé est ajouté à la base vectorielle, augmentant la robustesse et la précision des comparaisons futures (effet réseau de la donnée).

---

## Installation Rapide des Modules Principaux

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Module de Vérification de Documents

```bash
cd module-verification-docs
pip install -r requirements.txt
python main.py
```

Note : Tesseract OCR et Qdrant doivent être installés et configurés au préalable.

---

Projet réalisé dans le cadre du développement d'une plateforme intelligente d'aide à la décision pour l'analyse de prêts, la détection de fraude et l'analyse comportementale multi-canale.

---

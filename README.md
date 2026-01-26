# CreditSense AI

CreditSense AI est une plateforme intelligente d’analyse de prêts et d’aide à la prise de décision destinée aux analystes financiers.
Elle permet de centraliser les demandes de crédit, d’évaluer les risques, de détecter la fraude documentaire, d’analyser les messages textuels et vocaux, et de fournir des recommandations explicables basées sur l’intelligence artificielle.

---

## Vision Générale

La plateforme vise à assister les analystes dans :

* l’évaluation du risque crédit,
* la détection de fraudes (documents, messages, comportements),
* la centralisation des données multi-sources (documents, emails, WhatsApp, audio),
* la justification claire des décisions prises par l’IA.

---

## Structure du Projet

### 1. Frontend (version synthétique)

Le frontend présente une vision globale de la plateforme CreditSense AI.

Fonctionnalités principales :

* Dashboard de suivi des prêts :

  * état du prêt,
  * alertes de risque,
  * décisions prises par les analystes.
* Page d’analyse détaillée (au clic sur un prêt) :

  * pourcentage de risque,
  * recommandation IA (accorder ou refuser le crédit),
  * justification de la décision (pourquoi oui / pourquoi non),
  * documents détectés comme fraudés avec leurs pourcentages de crédibilité.
* Section paramètres :

  * intégration d’APIs externes (emails, plateformes bancaires, etc.).
* Authentification des analystes (login sécurisé).

---

### 2. Module de Vérification de Documents (module-verification-docs)

Ce module permet de vérifier l’authenticité des documents d’identité tels que les cartes CIN et les passeports.

Fonctionnement :

* Les documents de référence sont transformés en vecteurs et stockés dans Qdrant.
* Les modèles OCR, CLIP et Sentence Transformers sont utilisés pour :

  * extraire le texte des documents,
  * analyser le contenu visuel,
  * convertir images et textes en représentations vectorielles.
* Lorsqu’un nouveau document est soumis, il est comparé aux vecteurs de référence afin de mesurer la similarité et détecter les fraudes ou incohérences.

Fonctionnalités :

* Détection du type de document (CIN, passeport, etc.).
* Analyse visuelle et textuelle.
* Score de similarité et crédibilité du document.
* Interface de test via menu déroulant.

---

### 3. Module de Calcul de Risque (Credit Scoring)

Ce module utilise le Machine Learning pour prédire la capacité d’un client à rembourser un prêt.

#### Présentation

Il s’appuie sur le jeu de données German Credit afin d’entraîner des modèles capables de classer une demande de crédit en deux catégories :

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

* `src/` : scripts de traitement et d’entraînement
* `data/` : données brutes et transformées
* `models/` : modèle final sauvegardé

Technologies utilisées :

* Python
* Pandas
* NumPy
* Scikit-learn (Random Forest, Régression Logistique)

---

### 4. Module de Vérification de Textes et Emails (NLP)

Ce module analyse les messages textuels (emails, WhatsApp, etc.) liés aux demandes de crédit afin d’en extraire les informations clés et de comprendre le contexte.

Fonctionnalités :

* Nettoyage avancé des messages (suppression du bruit, signatures, HTML).
* Analyse sémantique pour comprendre l’intention du client.
* Extraction d’entités :

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

  * `process_messages.py` : moteur d’analyse NLP
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

Lancer l’API :

```bash
uvicorn app.main:app --reload
```

Lancer le traitement NLP :

```bash
python scripts/process_messages.py
```

---

### 5. Module Audio (Analyse Comportementale)

Ce module traite et analyse les messages vocaux (notamment WhatsApp) afin d’extraire des indicateurs comportementaux utiles à l’analyse du risque.

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

Projet réalisé dans le cadre du développement d’une plateforme intelligente d’aide à la décision pour l’analyse de prêts, la détection de fraude et l’analyse comportementale multi-canale.

---

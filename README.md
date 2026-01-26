# Credit Platform - Module 4

Plateforme de gestion de crédit avec intégration Gmail et MongoDB.

##  Structure du Projet

```
credit_platform/
├─ temp_files/      # Stockage des pièces jointes
├─ scripts/         # Scripts Python (Gmail, etc.)
├─ logs/            # Fichiers de logs
├─ app/             # Code FastAPI
│  └─ main.py       # API principale
├─ requirements.txt # Dépendances Python
└─ .env.example     # Variables d'environnement
```

##  Installation

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer MongoDB

Assurez-vous que MongoDB est en cours d'exécution sur `localhost:27017` ou configurez `MONGO_URI` dans un fichier `.env`.

### 3. Configurer Gmail API

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet
3. Activez **Gmail API**
4. Créez des credentials **OAuth 2.0**
5. Téléchargez le fichier JSON et renommez-le en `credentials.json`
6. Placez `credentials.json` dans le dossier `scripts/`

##  Utilisation

### Lancer l'API FastAPI

```bash
uvicorn app.main:app --reload
```

L'API sera accessible sur:
- **API**: http://127.0.0.1:8000
- **Documentation Swagger**: http://127.0.0.1:8000/docs

### Récupérer les emails Gmail

```bash
cd scripts
python gmail_fetch.py
```

Ce script va:
1.  Authentifier via OAuth (première fois uniquement)
2.  Récupérer les emails de votre boîte de réception
3.  Télécharger les pièces jointes dans `temp_files/`
4.  Envoyer chaque email à l'API FastAPI → MongoDB

### Récupérer les messages WhatsApp

**Configuration requise:** Voir [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)

```bash
cd scripts
python whatsapp_fetch.py
```

**Mode Webhook (recommandé):**
- Les messages sont automatiquement reçus via webhook
- Configurez l'URL webhook dans Meta Business Suite
- Le endpoint `/webhook/whatsapp` traite automatiquement les messages

**Types de messages supportés:**
-  Texte, Images, Documents, Audio, Vidéo

### Récupérer les transactions bancaires

**Configuration requise:** Voir [BANK_SETUP.md](BANK_SETUP.md)

```bash
cd scripts
python bank_fetch.py
```

Ce script va:
1.  S'authentifier auprès de l'API bancaire
2.  Récupérer les transactions
3.  Télécharger les documents associés
4.  Envoyer chaque transaction à l'API FastAPI → MongoDB

**Note:** Le script est générique et doit être adapté à votre plateforme bancaire spécifique.

## 📡 Endpoints API

### POST `/messages/`

Crée un nouveau message dans MongoDB.

**Corps de la requête:**
```json
{
  "source": "gmail | whatsapp | bank_platform",
  "sender": "example@gmail.com",
  "client_id": null,
  "timestamp": "2026-01-22T23:00:00",
  "subject": "Demande de crédit",
  "content_text": "Contenu du message...",
  "attachments": ["/path/to/file.pdf"],
  "metadata": {},
  "status": "raw"
}
```

### GET `/messages/`

Récupère les messages depuis MongoDB avec filtres optionnels.

**Paramètres de requête:**
- `source` (optionnel): Filtrer par source (gmail, whatsapp, bank_platform)
- `status` (optionnel): Filtrer par statut (raw, processed, etc.)
- `limit` (optionnel): Nombre maximum de résultats (défaut: 100)

**Exemple:**
```bash
curl "http://127.0.0.1:8000/messages/?source=whatsapp&limit=10"
```

### POST `/webhook/whatsapp`

Reçoit les messages WhatsApp via webhook (configuré dans Meta Business Suite).

### GET `/webhook/whatsapp`

Vérifie le webhook WhatsApp (requis par Meta).

##  Authentification

### Gmail (première exécution)

Lors de la première exécution de `gmail_fetch.py`:
1. Une fenêtre de navigateur s'ouvrira
2. Connectez-vous avec votre compte Gmail
3. Autorisez l'application
4. Un fichier `token.json` sera créé pour les prochaines exécutions

### WhatsApp

Configuration via Meta Business Suite - voir [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)

### Plateforme Bancaire

Configuration selon votre API bancaire - voir [BANK_SETUP.md](BANK_SETUP.md)

##  Intégrations Disponibles

| Source | Script | Mode | Status |
|--------|--------|------|--------|
| Gmail | `gmail_fetch.py` | Pull (polling) | ✅ Prêt |
| WhatsApp | `whatsapp_fetch.py` | Push (webhook) | ✅ Prêt |
| Plateforme Bancaire | `bank_fetch.py` | Pull/Push (adaptable) | ⚙️ À configurer |

##  Notes

- Les pièces jointes sont stockées dans `temp_files/`
- Les messages sont automatiquement envoyés à l'API FastAPI
- MongoDB stocke tous les messages dans la collection `messages`
- Tous les scripts supportent un mode test avec données simulées

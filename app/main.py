from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
import os
import sys

# Ajouter le dossier scripts au path pour importer les modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

app = FastAPI(title="Credit Platform – Module 4")

# MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client['creditapp']
collection = db['messages']

# Modèle Pydantic
from app.models import Message

@app.post("/messages/")
def create_message(msg: Message):
    """Stocke un message dans MongoDB."""
    collection.insert_one(msg.dict())
    return {"message": "Message stocké avec succès"}

@app.get("/messages/")
def get_messages(source: str = None, status: str = None, limit: int = 100):
    """Récupère les messages depuis MongoDB avec filtres optionnels."""
    query = {}
    if source:
        query["source"] = source
    if status:
        query["status"] = status
    
    messages = list(collection.find(query).limit(limit))
    
    # Convertir ObjectId en string pour la sérialisation JSON
    for msg in messages:
        msg["_id"] = str(msg["_id"])
    
    return {"count": len(messages), "messages": messages}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Webhook pour recevoir les messages WhatsApp.
    À configurer dans Meta Business Suite.
    """
    try:
        # Import du module WhatsApp
        from whatsapp_fetch import handle_webhook
        
        data = await request.json()
        success = handle_webhook(data)
        
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Erreur de traitement")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """
    Vérification du webhook WhatsApp (requis par Meta).
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "your_verify_token")
    
    if mode == "subscribe" and token == verify_token:
        return int(challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

@app.get("/")
def root():
    """Endpoint de santé."""
    return {
        "message": "API Credit Platform Module 4 en fonctionnement",
        "endpoints": {
            "POST /messages/": "Créer un message",
            "GET /messages/": "Récupérer les messages",
            "POST /webhook/whatsapp": "Webhook WhatsApp",
            "GET /webhook/whatsapp": "Vérification webhook WhatsApp"
        }
    }

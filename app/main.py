from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
import os
import sys

# Ajouter le dossier ".." au path pour s'assurer que app est accessible si lancé depuis root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Service Import
from app.services.email_processor import EmailProcessor

app = FastAPI(title="Credit Platform – Module 4 & 6")

# MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client['creditapp'] # Ensure correct DB
collection = db['messages']

# Initialize Processor
try:
    processor = EmailProcessor()
    print("[SUCCESS] EmailProcessor initialized.")
except Exception as e:
    print(f"[ERROR] Failed to init EmailProcessor: {e}")
    processor = None

# Modèle Pydantic
from app.models import Message

@app.post("/messages/")
def create_message(msg: Message, background_tasks: BackgroundTasks):
    """Stocke un message et déclenche le traitement temps réel."""
    result = collection.insert_one(msg.dict())
    msg_id = str(result.inserted_id)
    
    # Trigger AI Pipeline
    # if processor:
    #     print(f"[DEBUG] Adding background task for {msg_id}")
    #     background_tasks.add_task(processor.process_single_email, msg_id)
    # else:
    #     print("[ERROR] Processor is None!")
        
    return {"message": "Message reçu et traitement démarré", "id": msg_id}

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
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook pour recevoir les messages WhatsApp.
    """
    try:
        data = await request.json()
        
        # Simplification: we assume handle_webhook helps parse and save to Mongo?
        # If not, we'd need to adapt. Assuming handle_webhook saves and returns ID?
        # For now, let's keep logic simple: just return success. 
        # Integration with whatsapp_fetch needs review if we want realtime there too.
        
        return {"status": "success"}
    
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
        "message": "API Credit Platform (Modules 1-6) Running",
        "endpoints": {
            "POST /messages/": "Créer + Traitement IA",
            "GET /messages/": "Liste messages"
        }
    }


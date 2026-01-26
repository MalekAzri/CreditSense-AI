from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

app = FastAPI(title="Credit Platform – Module 4 (Version Simple)")

# Fichier JSON pour stocker les messages (au lieu de MongoDB)
MESSAGES_FILE = "messages_data.json"

# Modèle Pydantic
class Message(BaseModel):
    source: str
    sender: str
    client_id: Optional[str] = None
    timestamp: str
    subject: Optional[str] = None
    content_text: str
    attachments: List[str] = []
    metadata: dict = {}
    status: str = "raw"

def load_messages():
    """Charge les messages depuis le fichier JSON."""
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_messages(messages):
    """Sauvegarde les messages dans le fichier JSON."""
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

@app.post("/messages/")
def create_message(msg: Message):
    """Stocke un message dans le fichier JSON."""
    messages = load_messages()
    
    # Ajouter un ID et timestamp
    message_dict = msg.dict()
    message_dict['_id'] = f"msg_{len(messages) + 1}"
    message_dict['created_at'] = datetime.now().isoformat()
    
    messages.append(message_dict)
    save_messages(messages)
    
    return {"message": "Message stocké avec succès", "id": message_dict['_id']}

@app.get("/messages/")
def get_messages(source: str = None, status: str = None, limit: int = 100):
    """Récupère les messages depuis le fichier JSON avec filtres optionnels."""
    messages = load_messages()
    
    # Filtrer par source
    if source:
        messages = [m for m in messages if m.get('source') == source]
    
    # Filtrer par status
    if status:
        messages = [m for m in messages if m.get('status') == status]
    
    # Limiter les résultats
    messages = messages[-limit:]
    
    return {"count": len(messages), "messages": messages}

@app.get("/")
def root():
    """Endpoint de santé."""
    return {
        "message": "API Credit Platform Module 4 (Version Simple - Sans MongoDB)",
        "endpoints": {
            "POST /messages/": "Créer un message",
            "GET /messages/": "Récupérer les messages"
        },
        "storage": "Fichier JSON (messages_data.json)"
    }

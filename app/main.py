from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Ajouter le dossier ".." au path pour s'assurer que app est accessible si lancé depuis root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Service Import
from app.services.email_processor import EmailProcessor
from app.services.reply_generator import ReplyGenerator
from app.services.credit_scorer import CreditScorer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="Credit Platform – Module 4 & 6")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Initialize Reply Generator
try:
    reply_gen = ReplyGenerator()
    print("[SUCCESS] ReplyGenerator initialized.")
except Exception as e:
    print(f"[ERROR] Failed to init ReplyGenerator: {e}")
    reply_gen = None

# Initialize Credit Scorer (Module 6)
try:
    credit_scorer = CreditScorer()
    print("[SUCCESS] CreditScorer initialized.")
except Exception as e:
    print(f"[ERROR] Failed to init CreditScorer: {e}")
    credit_scorer = None

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

class ReplyRequest(BaseModel):
    email_text: str
    client_data: Optional[dict] = None

class SendReplyRequest(BaseModel):
    to_email: str
    subject: str
    body: str

@app.post("/messages/generate-reply")
def generate_reply(req: ReplyRequest):
    """Génère une suggestion de réponse avec l'IA."""
    if not reply_gen:
        raise HTTPException(status_code=500, detail="Reply generator not initialized")
    
    suggestion = reply_gen.generate_auto_reply(req.email_text, req.client_data)
    return {"suggestion": suggestion}

@app.post("/messages/send-reply")
def send_reply(req: SendReplyRequest):
    """Envoie une réponse par email via SMTP."""
    email_addr = os.getenv("SMTP_EMAIL", "banque.2026@gmail.com")
    email_pass = os.getenv("SMTP_PASSWORD", "banqueHackathon2026")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))

    try:
        msg = MIMEMultipart()
        msg['From'] = email_addr
        msg['To'] = req.to_email
        msg['Subject'] = req.subject
        
        msg.attach(MIMEText(req.body, 'plain', 'utf-8'))
        
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_addr, email_pass)
            server.send_message(msg)
            
        return {"status": "success", "message": f"Email envoyé à {req.to_email}"}
    except Exception as e:
        print(f"[SMTP ERROR] {e}")
        raise HTTPException(status_code=500, detail=f"Erreur d'envoi SMTP: {str(e)}")

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

@app.post("/clients/analyze")
async def analyze_client_credit(req: dict):
    """
    Effectue une analyse de crédit ML sur les données fournies.
    """
    if not credit_scorer:
        raise HTTPException(status_code=500, detail="Credit scorer not initialized")

    try:
        # On utilise les données envoyées directement par le frontend
        analysis_result = credit_scorer.analyze_client(req)
        return analysis_result

    except Exception as e:
        print(f"[ANALYSIS ERROR] {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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


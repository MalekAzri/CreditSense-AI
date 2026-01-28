import os
import base64
import requests
import time
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import email
from email.mime.text import MIMEText
from file_manager import file_manager
from message_logger import message_logger
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client[os.getenv("DB_NAME", "creditapp")]
collection = db.messages

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
API_URL = "http://127.0.0.1:8000/messages/"


def authenticate_gmail():
    """Authentifie l'utilisateur via OAuth et retourne le service Gmail."""
    creds = None
    
    # Obtenir le chemin absolu du dossier contenant ce script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, 'token.json')
    credentials_path = os.path.join(base_dir, 'credentials.json')
    
    # Le fichier token.json stocke les tokens d'accès et de rafraîchissement
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # Si les credentials n'existent pas ou sont invalides, demander à l'utilisateur de se connecter
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Le fichier '{credentials_path}' est introuvable. Veuillez le placer dans le dossier scripts/.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            # On utilise le port 8090 pour éviter les conflits
            creds = flow.run_local_server(port=8090)
        
        # Sauvegarder les credentials pour la prochaine exécution
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def download_attachment(service, user_id, msg_id, attachment_id, filename):
    """Télécharge une pièce jointe et la sauvegarde dans temp_files."""
    try:
        attachment = service.users().messages().attachments().get(
            userId=user_id, messageId=msg_id, id=attachment_id
        ).execute()
        
        file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
        
        # Utiliser le file_manager pour sauvegarder avec organisation
        file_path = file_manager.save_file(
            content=file_data,
            filename=filename,
            source='gmail',
            original_filename=filename
        )
        
        return file_path
    except Exception as e:
        print(f"Erreur lors du téléchargement de la pièce jointe {filename}: {e}")
        return None


def extract_email_body(payload):
    """Extrait le corps du message depuis le payload."""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html' and not body:
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    else:
        if 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    return body


def get_header_value(headers, name):
    """Récupère la valeur d'un header spécifique."""
    for header in headers:
        if header['name'].lower() == name.lower():
            return header['value']
    return None


def fetch_and_send_emails(max_results=10):
    """Récupère les emails depuis Gmail et les envoie à l'API FastAPI."""
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    try:
        service = authenticate_gmail()
        
        # Récupérer la liste des messages
        results = service.users().messages().list(
            userId='me', 
            maxResults=max_results,
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("Aucun message trouvé.")
            message_logger.log_fetch_start('gmail', count=0)
            message_logger.log_fetch_complete('gmail', 0, 0)
            return
        
        print(f"Nombre de messages trouvés: {len(messages)}")
        message_logger.log_fetch_start('gmail', count=len(messages))
        
        for msg_info in messages:
            # Récupérer les détails complets du message
            msg = service.users().messages().get(
                userId='me', 
                id=msg_info['id'],
                format='full'
            ).execute()
            
            headers = msg['payload']['headers']
            
            # Extraire les informations principales
            sender = get_header_value(headers, 'From')
            subject = get_header_value(headers, 'Subject')
            date = get_header_value(headers, 'Date')
            
            # Extraire le corps du message
            body = extract_email_body(msg['payload'])
            
            # Gérer les pièces jointes
            attachments = []
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['filename'] and 'attachmentId' in part['body']:
                        filename = part['filename']
                        attachment_id = part['body']['attachmentId']
                        
                        # Télécharger la pièce jointe
                        file_path = download_attachment(
                            service, 'me', msg_info['id'], 
                            attachment_id, filename
                        )
                        if file_path:
                            attachments.append(file_path)
            
            # Préparer le JSON pour l'API
            message_json = {
                "source": "gmail",
                "sender": sender,
                "client_id": None,  # À déterminer selon votre logique métier
                "timestamp": date or datetime.now().isoformat(),
                "subject": subject,
                "content_text": body,
                "attachments": attachments,
                "metadata": {
                    "message_id": msg_info['id'],
                    "thread_id": msg.get('threadId'),
                    "labels": msg.get('labelIds', [])
                },
                "status": "raw"
            }
            
            # Insérer directement dans MongoDB (Bypass API Instable)
            try:
                # Vérifier si l'email existe déjà (par message_id)
                exists = collection.find_one({"metadata.message_id": msg_info['id']})
                if exists:
                    print(f"[SKIP] Message déjà présent: {subject}")
                    continue
                
                result = collection.insert_one(message_json)
                msg_id = str(result.inserted_id)
                
                print(f"[OK] Message inséré directement dans Mongo: {subject} (ID: {msg_id})")
                
                # Message inséré avec succès
                success_count += 1
                
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Erreur lors de l'envoi à l'API: {e}")
                if hasattr(e.response, 'text'):
                    print(f"   Détails: {e.response.text}")
                
                # Logger l'erreur
                message_logger.log_message(
                    source='gmail',
                    sender=sender,
                    status='error',
                    attachments_count=len(attachments),
                    subject=subject,
                    error_msg=str(e)
                )
                error_count += 1
    
    except HttpError as error:
        print(f"Une erreur s'est produite avec l'API Gmail: {error}")
        message_logger.log_error('gmail', 'gmail_api_error', str(error))
    
    finally:
        # Logger la fin du fetch
        total_time = time.time() - start_time
        message_logger.log_fetch_complete('gmail', success_count, error_count, total_time)


if __name__ == "__main__":
    print("[INFO] Starting fetch...")
    fetch_and_send_emails(max_results=10)
    print("[SUCCESS] Process complete.")

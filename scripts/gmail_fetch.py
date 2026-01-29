import os
import sys
import io

# Force UTF-8 for Windows Console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
# from message_logger import message_logger
# from pymongo import MongoClient
# from dotenv import load_dotenv

# load_dotenv()
# client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
# db = client[os.getenv("DB_NAME", "creditapp")]
# collection = db.messages

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
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
            print("[AUTH] Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("[AUTH] No valid token found. Starting OAuth flow...")
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Le fichier '{credentials_path}' est introuvable. Veuillez le placer dans le dossier scripts/.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            # On utilise le port 8090 pour éviter les conflits
            # access_type='offline' et prompt='consent' garantissent l'obtention d'un refresh_token
            print("[AUTH] Opening browser for authentication on port 8090...")
            print("[AUTH] If the browser doesn't open, check for a popup or use the link below.")
            creds = flow.run_local_server(port=8090, access_type='offline', prompt='consent')
        
        # Sauvegarder les credentials pour la prochaine exécution
        print(f"[AUTH] Saving new token to {token_path}")
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds, static_discovery=False)


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



def fetch_and_return_emails(max_results=10):
    """Fetches emails from Gmail and returns them as a list of dicts."""
    start_time = time.time()
    fetched_emails = []
    
    try:
        service = authenticate_gmail()
        
        # Récupérer la liste des messages (uniquement les non-lus dans l'Innox)
        results = service.users().messages().list(
            userId='me', 
            maxResults=max_results,
            q='label:INBOX is:unread'
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("Aucun message trouvé.")
            return []
        
        print(f"Nombre de messages trouvés: {len(messages)}")
        
        for msg_info in messages:
            try:
                # Récupérer les détails complets du message
                msg = service.users().messages().get(
                    userId='me', 
                    id=msg_info['id'],
                    format='full'
                ).execute()
                
                # Marquer comme lu (supprimer le label UNREAD)
                service.users().messages().batchModify(
                    userId='me',
                    body={
                        'ids': [msg_info['id']],
                        'removeLabelIds': ['UNREAD']
                    }
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
                # (Attachment logic kept for future enablement, but path might need adjustment if running from root)
                
                # Préparer le JSON
                message_json = {
                    "source": "gmail",
                    "sender": sender,
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
                
                fetched_emails.append(message_json)
                
            except Exception as e:
                print(f"[ERROR] processing message {msg_info.get('id')}: {e}")
                continue
    
    except HttpError as error:
        print(f"Une erreur s'est produite avec l'API Gmail: {error}")
    
    finally:
        total_time = time.time() - start_time
        # Logging removed/simplified
        pass
        
    return fetched_emails


if __name__ == "__main__":
    print("[INFO] Starting fetch...")
    res = fetch_and_return_emails(max_results=5)
    print(f"[SUCCESS] Got {len(res)} emails")


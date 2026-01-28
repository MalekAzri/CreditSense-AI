import os
import base64
import time
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "creditapp")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db.messages

def authenticate_gmail():
    creds = None
    if os.path.exists('scripts/token.json'):
        creds = Credentials.from_authorized_user_file('scripts/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('scripts/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('scripts/token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def extract_email_body(payload):
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
            elif part['mimeType'] == 'text/html' and not body:
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    return body

def get_header_value(headers, name):
    for header in headers:
        if header['name'].lower() == name.lower():
            return header['value']
    return None

def fetch_and_save(max_results=10):
    try:
        service = authenticate_gmail()
        results = service.users().messages().list(userId='me', maxResults=max_results, labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("Aucun message trouvé.")
            return
            
        print(f"Messages trouvés: {len(messages)}")
        success = 0
        
        for msg_info in messages:
            msg = service.users().messages().get(userId='me', id=msg_info['id'], format='full').execute()
            headers = msg['payload']['headers']
            sender = get_header_value(headers, 'From')
            subject = get_header_value(headers, 'Subject')
            date = get_header_value(headers, 'Date')
            body = extract_email_body(msg['payload'])
            
            message_json = {
                "source": "gmail",
                "sender": sender,
                "timestamp": date,
                "subject": subject,
                "content_text": body,
                "metadata": {"message_id": msg_info['id']},
                "status": "raw"
            }
            
            # Check for duplicates
            if collection.find_one({"metadata.message_id": msg_info['id']}):
                print(f"[SKIP] Déjà présent: {subject}")
                continue
                
            collection.insert_one(message_json)
            print(f"[OK] Inséré: {subject}")
            success += 1
            
        print(f"Terminé. {success} nouveaux messages.")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    fetch_and_save(15)

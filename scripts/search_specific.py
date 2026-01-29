import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def search_email():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, 'token.json')
    
    if not os.path.exists(token_path):
        print(f"❌ Token not found at {token_path}")
        return

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    
    query = 'Demande de documents nécessaires pour un crédit'
    print(f"🔍 Searching for subject: '{query}'")
    results = service.users().messages().list(
        userId='me', 
        q=f'subject:("{query}")'
    ).execute()
    
    messages = results.get('messages', [])
    print(f"✅ Found {len(messages)} matching messages.")
    
    if messages:
        for msg_info in messages:
            msg = service.users().messages().get(userId='me', id=msg_info['id']).execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
            labels = msg.get('labelIds', [])
            print(f"   - Subject: {subject} | Labels: {labels}")
    else:
        print("❌ No matching messages found.")

if __name__ == "__main__":
    search_email()

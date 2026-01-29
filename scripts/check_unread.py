import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def check_all_inbox():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, 'token.json')
    
    if not os.path.exists(token_path):
        print(f"❌ Token not found at {token_path}")
        return

    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    
    print("🔍 Searching for ANY emails in INBOX...")
    results = service.users().messages().list(
        userId='me', 
        q='label:INBOX'
    ).execute()
    
    messages = results.get('messages', [])
    print(f"✅ Found {len(messages)} total messages in INBOX.")
    
    if messages:
        for msg_info in messages[:5]:
            msg = service.users().messages().get(userId='me', id=msg_info['id']).execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
            labels = msg.get('labelIds', [])
            print(f"   - From: {sender} | Subject: {subject} | Labels: {labels}")
    else:
        print("❌ No messages found in INBOX.")

if __name__ == "__main__":
    check_all_inbox()

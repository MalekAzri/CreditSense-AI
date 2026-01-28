import sys
import os
sys.path.append(os.getcwd())
from scripts.gmail_fetch import authenticate_gmail

service = authenticate_gmail()
results = service.users().messages().list(userId='me', maxResults=10).execute()
messages = results.get('messages', [])

print(f"Total: {len(messages)}")
for m in messages:
    detail = service.users().messages().get(userId='me', id=m['id']).execute()
    subject = next((h['value'] for h in detail['payload']['headers'] if h['name'].lower() == 'subject'), 'N/A')
    date = next((h['value'] for h in detail['payload']['headers'] if h['name'].lower() == 'date'), 'N/A')
    print(f"ID: {m['id']} | Date: {date} | Subject: {subject}")

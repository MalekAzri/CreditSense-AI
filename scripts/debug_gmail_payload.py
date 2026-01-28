from gmail_fetch import authenticate_gmail
import json

service = authenticate_gmail()
results = service.users().messages().list(userId='me', maxResults=10).execute()
messages = results.get('messages', [])

print(f"Total messages listed: {len(messages)}")
for m in messages:
    detail = service.users().messages().get(userId='me', id=m['id']).execute()
    subject = ""
    for h in detail['payload']['headers']:
        if h['name'] == 'Subject': subject = h['value']
    print(f"ID: {m['id']} | Subject: {subject} | Labels: {detail.get('labelIds')}")


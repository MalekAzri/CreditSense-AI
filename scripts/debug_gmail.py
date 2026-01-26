import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds = None
    # Adjust path if needed
    if os.path.exists('scripts/token.json'):
        creds = Credentials.from_authorized_user_file('scripts/token.json', SCOPES)
    elif os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        print("⚠️ Token invalide ou expiré.")
        if creds and creds.expired and creds.refresh_token:
            print("Tentative de rafraîchissement...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Erreur refresh: {e}")
                return
        else:
            print("❌ Pas de token valide trouvé. Veuillez supprimer token.json et relancer l'auth.")
            return

    try:
        service = build('gmail', 'v1', credentials=creds)
        
        with open("debug_report.txt", "w", encoding="utf-8") as f:
            # 1. Verify Profile (Email Address)
            profile = service.users().getProfile(userId='me').execute()
            f.write(f"✅ Connecté au compte : {profile.get('emailAddress')}\n")
            f.write(f"   Messages Total : {profile.get('messagesTotal')}\n\n")

            # 2. Check Inbox
            f.write("🔍 Recherche des 5 derniers messages reçus (INBOX)...\n")
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
            messages = results.get('messages', [])

            if not messages:
                f.write("❌ Aucun message trouvé dans INBOX.\n")
            else:
                f.write(f"✅ {len(messages)} messages trouvés. Voici les sujets :\n")
                for msg in messages:
                    txt = service.users().messages().get(userId='me', id=msg['id']).execute()
                    headers = txt['payload']['headers']
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "Sans objet")
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), "Inconnu")
                    f.write(f"   - [{sender}] : {subject}\n")
    except Exception as e:
        with open("debug_report.txt", "w", encoding="utf-8") as f:
            f.write(f"❌ Erreur API : {e}\n")

if __name__ == '__main__':
    main()

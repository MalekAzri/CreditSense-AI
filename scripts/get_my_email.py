from gmail_fetch import authenticate_gmail

try:
    service = authenticate_gmail()
    profile = service.users().getProfile(userId='me').execute()
    print("EMAIL_ADDRESS:", profile['emailAddress'])
except Exception as e:
    print("ERROR:", e)

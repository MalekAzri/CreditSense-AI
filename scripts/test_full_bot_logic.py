import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_processor import EmailProcessor
from scripts.gmail_fetch import fetch_and_return_emails

logging.basicConfig(level=logging.INFO)

print("--- Testing EmailProcessor ---")
try:
    processor = EmailProcessor()
    print("✅ EmailProcessor initialized")
except Exception as e:
    print(f"❌ EmailProcessor failed: {e}")
    sys.exit(1)

print("\n--- Testing Gmail Fetch ---")
try:
    emails = fetch_and_return_emails(max_results=1)
    print(f"✅ Gmail Fetch returned {len(emails)} emails")
    if emails:
        print(f"   Sample Subject: {emails[0].get('subject')}")
except Exception as e:
    print(f"❌ Gmail Fetch failed: {e}")
    sys.exit(1)

print("\n--- Test Finished Successfully ---")

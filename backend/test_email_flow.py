import os
import sys
import requests
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_processor import EmailProcessor

def test_email_flow():
    # 1. Initialize Processor
    processor = EmailProcessor()
    
    # 2. Define Mock Email
    mock_email = {
        "subject": "Demande de renseignement - Inconnu",
        "sender": "John Doe <john.doe@unknown.com>",
        "content_text": """
        Bonjour,
        
        Je m'appelle Malek Azri (CIN: 09876543). 
        Je souhaiterais faire une demande de crédit immobilier pour un montant de 150000 DT.
        Je suis assez stressé car j'ai besoin d'une réponse rapide.
        
        Cordialement,
        Malek
        """,
        "metadata": {
            "message_id": "test_msg_999"
        }
    }
    
    print("\n--- [1] Processing Email via AI Backend ---")
    results = processor.process_email_data(mock_email)
    
    if results["status"] != "success":
        print(f"Error processing: {results}")
        return

    print(f"Found Intent: {results['similarity_results']['top_intent']}")
    print(f"Confidence: {results['similarity_results']['confidence']}")
    print(f"Extraction: {results['extracted_data']}")
    
    # 3. Send to Webhook
    print("\n--- [2] Sending Results to Frontend Webhook ---")
    webhook_url = "http://localhost:3000/api/webhook/email"
    
    try:
        response = requests.post(webhook_url, json=results)
        print(f"Webhook Status: {response.status_code}")
        print(f"Webhook Response: {response.json()}")
        
        if response.json().get("linkedClientId"):
            print(f"SUCCESS: Linked to Client ID {response.json()['linkedClientId']}")
        else:
            print("WARNING: Email saved but NOT linked. (Make sure a client with email malek.azri@insat.ucar.tn exists)")
            
    except Exception as e:
        print(f"Error calling webhook: {e}")

if __name__ == "__main__":
    test_email_flow()

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
        "subject": "Suivi de dossier - Crédit Amira Mabrouk",
        "sender": "amira.mabrouk@email.com",
        "content_text": """
        Bonjour,
        
        Je reviens vers vous concernant ma demande de crédit déposée la semaine dernière.
        Serait-il possible de connaître l'état d'avancement de mon dossier ? 
        
        Référence du dossier : REF-2026-AMIRA
        
        Merci d'avance pour votre aide.
        
        Cordialement,
        Amira Mabrouk
        """,
        "metadata": {
            "message_id": "test_msg_status_request"
        }
    }
    
    results = processor.process_email_data(mock_email)

    if not results or results.get("status") != "success":
        print(f"❌ CRITICAL ERROR: AI Processing failed: {results}")
        return

    print("\n" + "="*50)
    print("TEST RESULT (REAL-TIME)")
    print("="*50)
    print(f"Subject   : {results.get('subject')}")
    print(f"Sender    : {results.get('sender')}")
    print(f"Status    : {results.get('status', 'processed')}")
    
    extracted = results.get('extracted_data', {})
    client_info = extracted.get('client_info', {})

    print("\nEXTRACTED DATA (PHASE 1 & 2):")
    print(f"  Clean Text: {results.get('clean_text', 'N/A')[:50]}...")
    print(f"  Credit Type: {extracted.get('credit_type', 'None')}")
    print(f"  Amount: {extracted.get('amount', 'None')} {extracted.get('currency', 'None')}")
    print(f"  Client Name: {client_info.get('name', 'None')}")
    print(f"  Phone: {client_info.get('phone', 'None')}")
    print(f"  CIN: {client_info.get('cin', 'None')}")
    print(f"  Reference: {extracted.get('reference', 'None')}")
    
    sim = results.get('similarity_results', {})
    tone = sim.get('tone_estimation', {})
    
    print("\nAI ANALYSIS:")
    print(f"  Intent     : {sim.get('top_intent', 'UNKNOWN')}")
    print(f"  Confidence : {sim.get('confidence', 0.0)}")
    print(f"  Tone       : Urgency={tone.get('urgency', 0)}, Stress={tone.get('stress', 0)}, Seriousness={tone.get('seriousness', 0)}")
    print("="*50)

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

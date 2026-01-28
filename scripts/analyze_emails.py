#!/usr/bin/env python3
"""
Script pour analyser les emails bruts dans MongoDB
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

# Ajouter le dossier parent au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_processor import EmailProcessor

load_dotenv()

def main():
    # Connexion MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "creditapp")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    # Initialiser EmailProcessor
    print("🚀 Initialisation du processeur d'emails...")
    try:
        processor = EmailProcessor()
        print("✅ EmailProcessor initialisé avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return
    
    # Trouver tous les emails avec status="raw"
    raw_emails = list(db.messages.find({"status": "raw"}))
    
    if not raw_emails:
        print("ℹ️  Aucun email à analyser (status='raw')")
        return
    
    print(f"\n📧 {len(raw_emails)} email(s) à analyser:\n")
    
    # Analyser chaque email
    for i, email in enumerate(raw_emails, 1):
        email_id = str(email["_id"])
        subject = email.get("subject", "Sans sujet")
        sender = email.get("sender", "Inconnu")
        
        print(f"[{i}/{len(raw_emails)}] 📬 {subject}")
        print(f"    De: {sender}")
        print(f"    ID: {email_id}")
        
        # Analyser
        try:
            result = processor.process_single_email(email_id)
            
            if result.get("status") == "skipped_sent":
                print(f"    ⏭️  Email ENVOYÉ - Ignoré")
            elif result.get("status") == "success":
                print(f"    ✅ Analysé avec succès!")
                
                # Afficher les résultats
                if "extracted_data" in result:
                    data = result["extracted_data"]
                    print(f"    📝 Type de crédit: {data.get('credit_type', 'Non détecté')}")
                    print(f"    💰 Montant: {data.get('amount', 'Non détecté')} {data.get('currency', '')}")
                    
                    client_info = data.get("client_info", {})
                    if client_info.get("name"):
                        print(f"    👤 Nom: {client_info.get('name')}")
                    if client_info.get("cin"):
                        print(f"    🆔 CIN: {client_info.get('cin')}")
                    if client_info.get("phone"):
                        print(f"    📞 Téléphone: {client_info.get('phone')}")
                
                if "similarity" in result:
                    sim = result["similarity"]
                    print(f"    🎯 Intent détecté: {sim.get('top_intent', 'UNKNOWN')} (confiance: {sim.get('confidence', 0)})")
            else:
                print(f"    ⚠️  Statut: {result.get('status', 'unknown')}")
                
        except Exception as e:
            print(f"    ❌ Erreur: {e}")
        
        print()
    
    print("🎉 Analyse terminée!")

if __name__ == "__main__":
    main()

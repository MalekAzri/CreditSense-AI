#!/usr/bin/env python3
"""
Credit Platform Bot 🤖
-----------------------
Ce script automatise le cycle complet :
1. Récupération des emails (Gmail)
2. Analyse intelligente (AI)
3. Affichage des résultats en temps réel

Lancez-le et laissez-le tourner en arrière-plan !
"""
import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

# Ajouter le dossier parent au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_processor import EmailProcessor
from scripts.gmail_fetch import fetch_and_send_emails

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("CreditBot")

load_dotenv()

def main():
    print("\n" + "="*50)
    print("🤖 CREDIT PLATFORM BOT - DÉMARRAGE...")
    print("="*50 + "\n")
    
    # 1. Connexion DB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "creditapp")
    
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        logger.info("✅ Connexion MongoDB établie.")
    except Exception as e:
        logger.error(f"❌ Erreur connexion MongoDB: {e}")
        return

    # 2. Initialisation IA (Pre-loading models)
    logger.info("🧠 Chargement des modèles d'IA (peut prendre quelques secondes)...")
    try:
        processor = EmailProcessor()
        logger.info("✅ Modèles IA chargés et prêts !")
    except Exception as e:
        logger.error(f"❌ Erreur chargement IA: {e}")
        return

    print("\n🚀 LE BOT EST EN LIGNE ! En attente de nouveaux emails...\n")
    print("Appuyez sur Ctrl+C pour arrêter.\n")

    # 3. Boucle principale
    loop_count = 0
    try:
        while True:
            loop_count += 1
            # A. Fetch Emails
            try:
                # On capture stdout pour éviter de polluer l'affichage si fetch_and_send_emails est bavard
                # (Sauf s'il trouve des messages)
                logger.info(f"cycle #{loop_count}: Vérification Gmail...")
                
                # Note: fetch_and_send_emails insère déjà dans Mongo avec status="raw"
                fetch_and_send_emails(max_results=5)
                
            except Exception as e:
                logger.error(f"⚠️ Erreur fetch: {e}")

            # B. Check for RAW emails in MongoDB
            raw_emails = list(db.messages.find({"status": "raw"}))
            
            if raw_emails:
                print(f"\n📨 {len(raw_emails)} NOUVEAU(X) EMAIL(S) DÉTECTÉ(S) !\n")
                
                for email in raw_emails:
                    email_id = str(email["_id"])
                    subject = email.get("subject", "Sans sujet")
                    sender = email.get("sender", "Inconnu")
                    
                    print(f"   ▶ Analyse de : '{subject}' (De: {sender})")
                    
                    try:
                        # Process
                        result = processor.process_single_email(email_id)
                        
                        # Afficher résultat
                        if result.get("status") == "success":
                            data = result.get("extracted_data", {})
                            sim = result.get("similarity_results", {})
                            
                            print(f"      ✅ ANALYSE RÉUSSIE")
                            print(f"      👤 Client : {data.get('client_info', {}).get('name') or 'Non détecté'}")
                            print(f"      🆔 CIN    : {data.get('client_info', {}).get('cin') or 'Non détecté'}")
                            print(f"      💰 Montant: {data.get('amount') or '?'} {data.get('currency') or ''}")
                            print(f"      🏠 Type   : {data.get('credit_type') or 'Non détecté'}")
                            print(f"      🎯 But    : {sim.get('top_intent')} ({sim.get('confidence')}%)")
                            print("-" * 40)
                            
                        elif result.get("status") == "skipped_sent":
                            print(f"      ⏭️ Email envoyé par nous (Ignoré)")
                        else:
                            print(f"      ⚠️ Échec analyse: {result.get('error')}")
                            
                    except Exception as e:
                        logger.error(f"❌ Erreur processing {email_id}: {e}")
            
            # C. Wait
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du bot. À bientôt !")

if __name__ == "__main__":
    main()

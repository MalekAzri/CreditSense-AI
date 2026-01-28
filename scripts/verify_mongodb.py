"""
Script pour vérifier le contenu de MongoDB.
Affiche tous les messages stockés dans la base de données.
"""

import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Connexion MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['creditapp']
collection = db['messages']


def display_message_summary(msg):
    """Affiche un résumé d'un message."""
    print(f"\n{'='*70}")
    print(f"ID: {msg.get('_id')}")
    print(f"Source: {msg.get('source')}")
    print(f"Sender: {msg.get('sender')}")
    if msg.get('client_id'):
        print(f"Client ID: {msg.get('client_id')}")
    print(f"Timestamp: {msg.get('timestamp')}")
    if msg.get('subject'):
        print(f"Subject: {msg.get('subject')}")
    
    # Afficher un aperçu du contenu
    content = msg.get('content_text', '')
    if len(content) > 100:
        print(f"Content: {content[:100]}...")
    else:
        print(f"Content: {content}")
    
    # Pièces jointes
    attachments = msg.get('attachments', [])
    print(f"Attachments: {len(attachments)}")
    if attachments:
        for att in attachments[:3]:  # Afficher max 3 pièces jointes
            # Extraire juste le nom du fichier
            filename = os.path.basename(att)
            print(f"  - {filename}")
        if len(attachments) > 3:
            print(f"  ... et {len(attachments) - 3} de plus")
    
    print(f"Status: {msg.get('status')}")
    print(f"{'='*70}")


def verify_mongodb():
    """Vérifie et affiche tous les messages dans MongoDB."""
    print("🔍 Vérification de MongoDB...\n")
    
    try:
        # Tester la connexion
        client.server_info()
        print("✅ Connexion à MongoDB réussie")
        print(f"📊 Base de données: credit_platform")
        print(f"📦 Collection: messages\n")
        
        # Compter les messages
        total_count = collection.count_documents({})
        print(f"📨 Nombre total de messages: {total_count}\n")
        
        if total_count == 0:
            print("ℹ️  Aucun message trouvé dans la base de données")
            print("💡 Lancez les scripts d'intégration pour ajouter des messages:")
            print("   - cd scripts && python gmail_fetch.py")
            print("   - cd scripts && python whatsapp_fetch.py")
            print("   - cd scripts && python bank_fetch.py")
            return
        
        # Statistiques par source
        print("📊 Statistiques par source:")
        sources = collection.distinct('source')
        for source in sources:
            count = collection.count_documents({'source': source})
            print(f"   - {source}: {count} message(s)")
        
        print("\n" + "="*70)
        print("LISTE DES MESSAGES")
        print("="*70)
        
        # Récupérer et afficher tous les messages
        messages = collection.find().sort([('timestamp', -1)]).limit(20)
        
        for msg in messages:
            display_message_summary(msg)
        
        if total_count > 20:
            print(f"\n⚠️  Affichage des 20 derniers messages sur {total_count}")
        
        print(f"\n✅ Vérification terminée")
        
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à MongoDB: {e}")
        print(f"💡 Assurez-vous que MongoDB est en cours d'exécution sur {MONGO_URI}")


def show_stats():
    """Affiche des statistiques détaillées."""
    try:
        total = collection.count_documents({})
        
        # Stats par statut
        print("\n📈 Statistiques par statut:")
        statuses = collection.distinct('status')
        for status in statuses:
            count = collection.count_documents({'status': status})
            percentage = (count / total * 100) if total > 0 else 0
            print(f"   - {status}: {count} ({percentage:.1f}%)")
        
        # Messages avec pièces jointes
        with_attachments = collection.count_documents({'attachments': {'$ne': []}})
        print(f"\n📎 Messages avec pièces jointes: {with_attachments}")
        
        # Messages récents (dernières 24h)
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        recent = collection.count_documents({'timestamp': {'$gte': yesterday}})
        print(f"🕐 Messages des dernières 24h: {recent}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    verify_mongodb()
    show_stats()

#!/usr/bin/env python3
"""
Script pour supprimer les anciens emails de youssef.turki@ept.ucar.tn
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def main():
    # Connexion MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "creditapp")
    
    print("🔌 Connexion à MongoDB...")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    # Compter les emails à supprimer
    old_email = "youssef.turki@ept.ucar.tn"
    
    print(f"\n🔍 Recherche des emails de '{old_email}'...")
    
    count = db.messages.count_documents({
        "sender": {"$regex": old_email, "$options": "i"}
    })
    
    if count == 0:
        print(f"✅ Aucun email trouvé pour '{old_email}'")
        return
    
    print(f"📧 {count} email(s) trouvé(s) à supprimer")
    
    # Afficher quelques exemples
    print("\n📋 Exemples d'emails à supprimer:")
    examples = db.messages.find(
        {"sender": {"$regex": old_email, "$options": "i"}},
        {"subject": 1, "sender": 1, "timestamp": 1}
    ).limit(5)
    
    for i, email in enumerate(examples, 1):
        subject = email.get("subject", "Sans sujet")
        sender = email.get("sender", "Inconnu")
        print(f"  {i}. {subject[:50]}... (De: {sender})")
    
    # Confirmation
    print(f"\n⚠️  ATTENTION: {count} email(s) vont être SUPPRIMÉS définitivement!")
    response = input("Voulez-vous continuer? (oui/non): ").strip().lower()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return
    
    # Supprimer
    print("\n🗑️  Suppression en cours...")
    result = db.messages.delete_many({
        "sender": {"$regex": old_email, "$options": "i"}
    })
    
    print(f"✅ {result.deleted_count} email(s) supprimé(s) avec succès!")
    
    # Vérification
    remaining = db.messages.count_documents({
        "sender": {"$regex": old_email, "$options": "i"}
    })
    
    if remaining == 0:
        print(f"🎉 Nettoyage terminé! Aucun email de '{old_email}' ne reste dans la base.")
    else:
        print(f"⚠️  Attention: {remaining} email(s) restant(s)")
    
    # Afficher les statistiques finales
    total_emails = db.messages.count_documents({})
    print(f"\n📊 Total d'emails dans la base: {total_emails}")

if __name__ == "__main__":
    main()

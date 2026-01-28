from pymongo import MongoClient
import os
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

def view_latest():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client[os.getenv("DB_NAME", "creditapp")]
    
    # Récupérer le dernier email traité
    latest_email = db.messages.find_one(
        {"status": "processed"},
        sort=[("processed_at", -1)]
    )
    
    if not latest_email:
        print("Aucun email traité trouvé.")
        return

    print("\n📧 === RÉSULTAT DE L'ANALYSE === 📧\n")
    print(f"Suject: {latest_email.get('subject')}")
    print(f"De: {latest_email.get('sender')}")
    print("-" * 50)
    print(f"Contenu (nettoyé): \n{latest_email.get('clean_text')}")
    print("-" * 50)
    
    data = latest_email.get('extracted_data', {})
    print("\n📊 DONNÉES EXTRAITES:")
    print(f"   💰 Montant: {data.get('amount')} {data.get('currency')}")
    print(f"   📝 Type: {data.get('credit_type')}")
    
    client = data.get('client_info', {})
    print(f"   👤 Nom: {client.get('name')}")
    print(f"   🆔 CIN: {client.get('cin')}")
    print(f"   📞 Tél: {client.get('phone')}")
    print(f"   📧 Email: {client.get('email')}")
    
    sim = latest_email.get('similarity_results', {})
    print("\n🧠 INTELLIGENCE ARTIFICIELLE:")
    print(f"   🎯 Intention: {sim.get('top_intent')}")
    print(f"   🤖 Confiance: {sim.get('confidence')}")
    
    tone = sim.get('tone_estimation', {})
    print(f"   mood: Urgence={tone.get('urgency')}/5, Stress={tone.get('stress')}/5")

if __name__ == "__main__":
    view_latest()

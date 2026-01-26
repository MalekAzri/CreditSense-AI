import json
import random
import uuid
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.models import SyntheticEmail, Tone

# Configuration
OUTPUT_FILE = "synthetic_emails.json"
TARGET_COUNTS = {
    "CREDIT_REQUEST": 25,
    "INFO_REQUEST": 15,
    "FOLLOW_UP": 15,
    "OTHER_CREDIT": 10,
    "NOT_RELEVANT": 15
}

# --- Data Pools ---

# 1. CREDIT_REQUEST
CREDIT_TEMPLATES = [
    "Bonjour, je souhaiterais obtenir un crédit de {amount} {currency} pour {reason}.",
    "Salut, j'ai besoin d'un financement pour {reason}. Montant: {amount} {currency}.",
    "Madame, Monsieur, je voudrais faire une demande de prêt. J'ai besoin de {amount} {currency}.",
    "Je veux acheter {reason_direct} et il me manque {amount} {currency}.",
    "Est-il possible d'emprunter {amount} {currency} sur 5 ans pour {reason} ?",
    "Besoin urgent de {amount} {currency} pour {reason}. Merci de m'aider.",
    "Je cherche un crédit {type_credit} de {amount} {currency}.",
    "Pourriez-vous m'accorder un prêt de {amount} {currency} ?",
    "Dossier de demande de crédit : {amount} {currency} pour {reason}.",
    "Financement {type_credit} souhaité : {amount} {currency}."
]

REASONS = [
    "l'achat d'une voiture", "construire ma maison", "un voyage de noces", 
    "rénover mon appartement", "payer les études de mon fils", "un projet professionnel",
    "acheter de l'équipement industriel", "changer de véhicule", "un besoin de trésorerie"
]

REASONS_DIRECT = [
    "une nouvelle cuisine", "une BMW occasion", "un terrain à bizerte", 
    "des machines pour mon usine", "un camion de livraison"
]

CURRENCIES = ["DT", "TND", "dinars", "millimes"]

# 2. INFO_REQUEST
INFO_TEMPLATES = [
    "Quels sont vos taux pour un crédit immobilier ?",
    "C'est quoi le taux d'intérêt actuel ?",
    "Bonjour, quels documents faut-il pour un prêt auto ?",
    "Est-ce que vous financez les startups ?",
    "Je voudrais savoir si je suis éligible au crédit consommation.",
    "Quelles sont les conditions pour un rachat de crédit ?",
    "Avez-vous une agence à Sousse ?",
    "Comment se passe le remboursement anticipé ?",
    "C'est quoi la durée maximale de remboursement ?",
    "Pouvez-vous m'envoyer une simulation pour 20000 DT ?"
]

# 3. FOLLOW_UP (Relance / Suivi)
FOLLOW_UP_TEMPLATES = [
    "Bonjour, où en est mon dossier n°{ref} ?",
    "Je n'ai pas eu de nouvelles de ma demande de la semaine dernière.",
    "Est-ce que mon crédit a été accepté ?",
    "J'attends toujours votre réponse pour le dossier {ref}.",
    "C'est urgent, avez-vous traité ma demande ?",
    "Je vous ai envoyé les pièces manquantes hier.",
    "Pourquoi c'est si long ? Dossier référence {ref}.",
    "Merci de me tenir informé de l'avancement.",
    "Je reviens vers vous concernant ma demande de prêt.",
    "Avez-vous bien reçu mon CIN ?"
]

# 4. OTHER_CREDIT (Rachat, Leasing, etc.)
OTHER_TEMPLATES = [
    "Je voudrais faire un rachat de mes crédits en cours.",
    "Est-ce que vous faites du leasing pour les voitures ?",
    "Je veux regrouper mes dettes en une seule mensualité.",
    "Proposez-vous de la LOA ?",
    "Je cherche une solution pour réduire mes mensualités.",
    "Rachat de crédit immobilier possible ?"
]

# 5. NOT_RELEVANT (Spam, Erreur, Autre)
IRRELEVANT_TEMPLATES = [
    "Ceci est une offre de partenariat commercial.",
    "Veuillez trouver ci-joint ma facture d'électricité.",
    "Bonne année à toute l'équipe !",
    "Désabonnez-moi de votre liste.",
    "Je me suis trompé de destinataire, désolé.",
    "Offre exceptionnelle sur les panneaux solaires.",
    "URGENT : Votre compte Netflix va expirer.",
    "Bonjour, vendez-vous des assurances vie ?",
    "Test message 123.",
    "Merci pour votre accueil hier."
]

# --- Generators ---

def generate_tone(intent):
    """Generate somewhat realistic tone scores based on intent."""
    seriousness = round(random.uniform(0.5, 1.0), 2)
    stress = round(random.uniform(0.0, 0.4), 2)
    urgency = round(random.uniform(0.0, 0.4), 2)
    
    if intent == "CREDIT_REQUEST":
        seriousness = round(random.uniform(0.7, 1.0), 2)
        urgency = round(random.uniform(0.2, 0.8), 2) # Often urgent
    elif intent == "FOLLOW_UP":
        stress = round(random.uniform(0.4, 0.9), 2) # Stressed if waiting
        urgency = round(random.uniform(0.5, 1.0), 2)
    elif intent == "NOT_RELEVANT":
        seriousness = round(random.uniform(0.0, 0.5), 2)
        
    return Tone(seriousness=seriousness, stress=stress, urgency=urgency)

def generate_text(intent):
    if intent == "CREDIT_REQUEST":
        tmpl = random.choice(CREDIT_TEMPLATES)
        amount = random.choice([5000, 10000, 25000, 50000, 100000, 200]) # 200k in mills sometimes handled downstream
        curr = random.choice(CURRENCIES)
        
        # Handle different placeholders
        text = tmpl.replace("{amount}", str(amount)).replace("{currency}", curr)
        text = text.replace("{reason}", random.choice(REASONS))
        text = text.replace("{reason_direct}", random.choice(REASONS_DIRECT))
        text = text.replace("{type_credit}", random.choice(["immo", "auto", "conso", "pro"]))
        
        # Add some noise/variations
        if random.random() > 0.8: text = text.lower()
        if random.random() > 0.9: text = text.upper() # Shouting
        return text
        
    elif intent == "INFO_REQUEST":
        return random.choice(INFO_TEMPLATES)
        
    elif intent == "FOLLOW_UP":
        ref = f"REF-{random.randint(1000,9999)}"
        return random.choice(FOLLOW_UP_TEMPLATES).replace("{ref}", ref)
        
    elif intent == "OTHER_CREDIT":
        return random.choice(OTHER_TEMPLATES)
        
    elif intent == "NOT_RELEVANT":
        return random.choice(IRRELEVANT_TEMPLATES)
    
    return "Bonjour"

def generate_synthetic_data():
    emails = []
    
    for intent, count in TARGET_COUNTS.items():
        for i in range(count):
            text = generate_text(intent)
            tone = generate_tone(intent)
            
            # Create object adhering to SyntheticEmail schema
            email_obj = SyntheticEmail(
                synthetic_id=f"syn_{uuid.uuid4().hex[:8]}",
                source="synthetic",
                sender=f"user_{random.randint(100,999)}@example.com",
                timestamp=(datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                content_text=text,
                subject=f"Sujet: {intent}", # Simple subject
                status="training_data",
                intent=intent,
                tone=tone,
                attachments=[],
                metadata={"generated": True}
            )
            
            # Hack: Pydantic .dict() or model_dump()
            emails.append(email_obj.dict())

    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Generated {len(emails)} synthetic emails in '{OUTPUT_FILE}'.")
    print("Distribution:")
    for intent, count in TARGET_COUNTS.items():
        print(f"  - {intent}: {count}")

if __name__ == "__main__":
    generate_synthetic_data()

import sys
import os

# Ajout du chemin pour permettre les imports depuis src
sys.path.append(os.getcwd())

from src.agent_logic import CreditSenseAgent

def run_tests():
    agent = CreditSenseAgent()
    
    scenarios = [
        {
            "name": "STATUT - Identifié par EMAIL (Individuel)",
            "email": "Bonjour, c'est Jean Dupont (jean.dupont@email.com). Quel est mon statut ?",
            "check": ["Jean Dupont", "En attente de documents", "Profil Individuel"]
        },
        {
            "name": "DOCUMENTS - Identifié par ID (Individuel)",
            "email": "Que manque-t-il à mon dossier CS-003 ?",
            "check": ["Philippe Legrand", "Bulletin bancaire", "Relevés bancaires", "Domicile"]
        },
        {
            "name": "STATUT - Identifié par EMAIL (PME)",
            "email": "Status update for acme.corp@email.com please.",
            "check": ["Acme Corp", "En attente", "Profil PME"]
        },
        {
            "name": "DOCUMENTS - Identifié par ID (PME)",
            "email": "Quelles sont les pièces manquantes pour PME-001 ?",
            "check": ["Acme Corp", "Matricule fiscal", "Compte de résultat"]
        },
        {
            "name": "DOSSIER COMPLET - (Individuel)",
            "email": "Bonjour, Marie Curie ici (marie.curie@email.com). Est-ce que tout est bon ?",
            "check": ["Marie Curie", "Approuvé", "dossier est complet"]
        },
        {
            "name": "CLIENT INCONNU - (Mais intention reconnue)",
            "email": "Bonjour, je voudrais savoir quels documents envoyer pour un nouveau prêt ?",
            "check": ["Besoin de documents spécifiques", "Client Individuel", "Client PME"]
        },
        {
            "name": "AUTRE - (Intention hors sujet)",
            "email": "Bonjour, je voudrais prendre un rendez-vous demain.",
            "check": ["Merci pour votre message", "conseiller CreditSense reviendra vers vous"]
        }
    ]

    print("="*60)
    print("DEMARRAGE DES TESTS UNIFIES - CREDITSENSE AI")
    print("="*60)

    for i, test in enumerate(scenarios, 1):
        print(f"\nTEST {i}: {test['name']}")
        print(f"INPUT : {test['email']}")
        
        response = agent.process_email(test['email'])
        
        print(f"RESPONSE IA :\n{response}")
        
        # Vérification des mots-clés
        success = True
        for keyword in test['check']:
            if keyword.lower() not in response.lower():
                print(f"FAILED : Mot-clé '{keyword}' manquant.")
                success = False
        
        if success:
            print("OK")
        
        print("-" * 40)

    print("\n" + "="*60)
    print("FIN DES TESTS")
    print("="*60)

def interactive_mode():
    agent = CreditSenseAgent()
    print("\n" + "="*60)
    print("MODE INTERACTIF - CREDITSENSE AI")
    print("Entrez vos questions pour tester les reponses dynamiques.")
    print("Tapez 'q' pour quitter.")
    print("="*60)
    
    while True:
        user_input = input("\nVotre Email/Question : ")
        if user_input.lower() == 'q':
            break
        if user_input.strip():
            response = agent.process_email(user_input)
            print(f"\nREPONSE IA :\n{response}")
            print("-" * 40)

if __name__ == "__main__":
    try:
        # On propose de lancer les tests automatiques ou de passer en direct
        choice = input("Voulez-vous lancer les tests automatiques d'abord ? (o/n) : ")
        if choice.lower() == 'o':
            run_tests()
        
        interactive_mode()
    except Exception as e:
        print(f"Erreur critique : {e}")

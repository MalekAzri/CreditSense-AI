import os
import requests
import json

def test_qdrant_and_reply():
    print("🚀 DÉMARRAGE DES TESTS - CreditSense AI\n")

    # 1. Vérification du Backend
    BASE_URL = "http://localhost:8000" # Assurez-vous que FastAPI tourne
    
    print("--- [1] Test de Connexion & Génération de Réponse AI ---")
    
    # Simuler un email de demande de crédit d'un client dont on n'a pas les docs
    test_payload = {
        "email_text": "Bonjour, je voudrais savoir où en est ma demande de crédit. Mon nom est Malek Azri.",
        "client_data": {
            "nom": "Malek",
            "typeClient": "individu",
            "doc_identite": None, # Manquant
            "doc_demande_credit": "http://link-to-doc.pdf", # Présent
            "doc_bilan_3ans": None # Manquant pour Individu? (Selon schema: Bilan est PME, mais vérifions la logique)
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/messages/generate-reply", json=test_payload)
        if response.status_code == 200:
            reply = response.json().get("reply")
            print("✅ TEST RÉUSSI : Réponse IA générée avec succès")
            print(f"\nSuggestion de l'IA :\n{'-'*20}\n{reply}\n{'-'*20}")
            
            if "copie de votre pièce d'identité" in reply.lower() or "manque encore les documents" in reply.lower():
                print("\n🔥 VÉRIFICATION : L'IA a correctement détecté les pièces manquantes !")
            else:
                print("\n⚠️ ATTENTION : L'IA n'a pas listé de documents. Vérifiez si le client est bien considéré comme incomplet.")
        else:
            print(f"❌ ÉCHEC : Le serveur a répondu {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ ERREUR : Impossible de contacter le backend FastAPI sur {BASE_URL}")
        print("Assurez-vous de lancer le backend avec : python scripts/start_bot.py (ou votre script de démarrage)")

    print("\n--- [2] Rappel des Étapes de Test Manuel (Dashboard) ---")
    print("1. Ouvrez le dashboard : http://localhost:3000/dashboard")
    print("2. Allez dans 'Communications' (emails orphelins).")
    print("3. Cliquez sur un mail, puis sur 'Réponse Auto'.")
    print("4. Vérifiez que la modale s'ouvre avec un texte pré-rempli intelligemment.")

if __name__ == "__main__":
    test_qdrant_and_reply()

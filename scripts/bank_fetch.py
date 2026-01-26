import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import time
from file_manager import file_manager
from message_logger import message_logger

# Charger les variables d'environnement
load_dotenv()

# Configuration API Bancaire
# Adaptez ces variables selon votre plateforme bancaire
BANK_API_URL = os.getenv("BANK_API_URL", "https://api.bank.example.com/v1")
BANK_API_KEY = os.getenv("BANK_API_KEY")
BANK_API_SECRET = os.getenv("BANK_API_SECRET")

# Configuration API FastAPI
API_URL = "http://127.0.0.1:8000/messages/"


def authenticate_bank_api():
    """
    Authentifie auprès de l'API bancaire.
    Adaptez cette fonction selon votre plateforme bancaire.
    """
    try:
        # Exemple générique - à adapter selon votre API
        auth_url = f"{BANK_API_URL}/auth/token"
        payload = {
            "api_key": BANK_API_KEY,
            "api_secret": BANK_API_SECRET
        }
        
        response = requests.post(auth_url, json=payload)
        response.raise_for_status()
        
        token = response.json().get("access_token")
        print(f"✅ Authentification réussie auprès de l'API bancaire")
        return token
    
    except Exception as e:
        print(f"❌ Erreur d'authentification: {e}")
        return None


def fetch_bank_transactions(auth_token, limit=50):
    """
    Récupère les transactions depuis l'API bancaire.
    Adaptez cette fonction selon votre plateforme bancaire.
    """
    try:
        # Exemple générique - à adapter selon votre API
        transactions_url = f"{BANK_API_URL}/transactions"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        params = {
            "limit": limit,
            "status": "pending"  # Récupérer uniquement les transactions en attente
        }
        
        response = requests.get(transactions_url, headers=headers, params=params)
        response.raise_for_status()
        
        transactions = response.json().get("transactions", [])
        print(f"✅ {len(transactions)} transaction(s) récupérée(s)")
        return transactions
    
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des transactions: {e}")
        return []


def download_bank_document(auth_token, document_id, filename):
    """
    Télécharge un document depuis l'API bancaire.
    Adaptez cette fonction selon votre plateforme bancaire.
    """
    try:
        document_url = f"{BANK_API_URL}/documents/{document_id}"
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(document_url, headers=headers)
        response.raise_for_status()
        
        # Sauvegarder avec le file_manager
        file_path = file_manager.save_file(
            content=response.content,
            filename=filename,
            source='bank',
            original_filename=filename
        )
        
        print(f"✅ Document téléchargé: {filename}")
        return file_path
    
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement du document: {e}")
        return None


def process_bank_transaction(transaction, auth_token):
    """Traite une transaction bancaire et l'envoie à l'API FastAPI."""
    try:
        # Extraire les informations de la transaction
        # Adaptez ces champs selon votre API bancaire
        transaction_id = transaction.get("id")
        client_id = transaction.get("client_id") or transaction.get("customer_id")
        sender = transaction.get("client_name") or transaction.get("customer_name")
        amount = transaction.get("amount")
        currency = transaction.get("currency", "MAD")
        transaction_type = transaction.get("type", "credit_request")
        timestamp = transaction.get("created_at") or datetime.now().isoformat()
        description = transaction.get("description", "")
        
        # Construire le contenu du message
        content_text = f"""
Transaction bancaire - {transaction_type}
Montant: {amount} {currency}
Description: {description}
        """.strip()
        
        # Gérer les documents associés
        attachments = []
        documents = transaction.get("documents", [])
        for doc in documents:
            doc_id = doc.get("id")
            doc_name = doc.get("name") or f"document_{doc_id}.pdf"
            
            file_path = download_bank_document(auth_token, doc_id, doc_name)
            if file_path:
                attachments.append(file_path)
        
        # Préparer le JSON pour l'API
        message_json = {
            "source": "bank_platform",
            "sender": sender,
            "client_id": client_id,
            "timestamp": timestamp,
            "subject": f"Transaction bancaire - {amount} {currency}",
            "content_text": content_text,
            "attachments": attachments,
            "metadata": {
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": currency,
                "transaction_type": transaction_type,
                "original_data": transaction
            },
            "status": "raw"
        }
        
        # Envoyer à l'API FastAPI
        try:
            api_start = time.time()
            response = requests.post(API_URL, json=message_json)
            response.raise_for_status()
            api_time = (time.time() - api_start) * 1000
            
            print(f"✅ Transaction bancaire envoyée avec succès: {transaction_id}")
            print(f"   Client: {sender} - Montant: {amount} {currency}")
            print(f"   Réponse: {response.json()}")
            
            # Logger le succès
            message_logger.log_message(
                source='bank_platform',
                sender=sender,
                status='success',
                attachments_count=len(attachments),
                client_id=client_id,
                subject=f"Transaction {amount} {currency}"
            )
            message_logger.log_api_call('/messages/', response.status_code, api_time)
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de l'envoi à l'API: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Détails: {e.response.text}")
            
            # Logger l'erreur
            message_logger.log_message(
                source='bank_platform',
                sender=sender,
                status='error',
                attachments_count=len(attachments),
                client_id=client_id,
                error_msg=str(e)
            )
            return False
    
    except Exception as e:
        print(f"❌ Erreur lors du traitement de la transaction: {e}")
        message_logger.log_error('bank_platform', 'processing_error', str(e))
        return False


def fetch_and_send_bank_data():
    """Récupère les données bancaires et les envoie à l'API FastAPI."""
    print("🔄 Démarrage de la récupération des données bancaires...")
    start_time = time.time()
    
    # Authentification
    auth_token = authenticate_bank_api()
    if not auth_token:
        print("❌ Impossible de s'authentifier auprès de l'API bancaire")
        message_logger.log_error('bank_platform', 'authentication_error', 'Failed to authenticate')
        return
    
    # Récupération des transactions
    transactions = fetch_bank_transactions(auth_token)
    
    if not transactions:
        print("ℹ️  Aucune transaction à traiter")
        message_logger.log_fetch_start('bank_platform', count=0)
        message_logger.log_fetch_complete('bank_platform', 0, 0)
        return
    
    message_logger.log_fetch_start('bank_platform', count=len(transactions))
    
    # Traitement de chaque transaction
    success_count = 0
    for transaction in transactions:
        if process_bank_transaction(transaction, auth_token):
            success_count += 1
        time.sleep(0.5)  # Éviter de surcharger l'API
    
    # Logger la fin du fetch
    total_time = time.time() - start_time
    error_count = len(transactions) - success_count
    message_logger.log_fetch_complete('bank_platform', success_count, error_count, total_time)
    
    print(f"\n✅ Processus terminé: {success_count}/{len(transactions)} transactions envoyées avec succès")


def test_with_sample_data():
    """Fonction de test avec des données simulées."""
    print("🔄 Mode test avec des données simulées...")
    
    sample_transaction = {
        "id": "TXN123456",
        "client_id": "CLIENT001",
        "customer_name": "Ahmed Bennani",
        "amount": 50000,
        "currency": "MAD",
        "type": "credit_request",
        "description": "Demande de crédit immobilier",
        "created_at": datetime.now().isoformat(),
        "documents": []
    }
    
    # Simuler le traitement
    message_json = {
        "source": "bank_platform",
        "sender": sample_transaction["customer_name"],
        "client_id": sample_transaction["client_id"],
        "timestamp": sample_transaction["created_at"],
        "subject": f"Transaction bancaire - {sample_transaction['amount']} {sample_transaction['currency']}",
        "content_text": f"""
Transaction bancaire - {sample_transaction['type']}
Montant: {sample_transaction['amount']} {sample_transaction['currency']}
Description: {sample_transaction['description']}
        """.strip(),
        "attachments": [],
        "metadata": {
            "transaction_id": sample_transaction["id"],
            "amount": sample_transaction["amount"],
            "currency": sample_transaction["currency"],
            "transaction_type": sample_transaction["type"]
        },
        "status": "raw"
    }
    
    try:
        response = requests.post(API_URL, json=message_json)
        response.raise_for_status()
        print(f"✅ Transaction test envoyée avec succès")
        print(f"   Réponse: {response.json()}")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")


if __name__ == "__main__":
    if not BANK_API_KEY or not BANK_API_SECRET:
        print("⚠️  BANK_API_KEY et BANK_API_SECRET doivent être configurés dans .env")
        print("🔄 Exécution en mode test avec des données simulées...")
        test_with_sample_data()
    else:
        fetch_and_send_bank_data()

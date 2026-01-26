import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from file_manager import file_manager
from message_logger import message_logger

# Charger les variables d'environnement
load_dotenv()

# Configuration WhatsApp Business API
WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

# Configuration API FastAPI
API_URL = "http://127.0.0.1:8000/messages/"


def download_whatsapp_media(media_id, filename):
    """Télécharge un fichier média depuis WhatsApp."""
    try:
        # Étape 1: Récupérer l'URL du média
        media_url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        
        response = requests.get(media_url, headers=headers)
        response.raise_for_status()
        media_data = response.json()
        
        # Étape 2: Télécharger le fichier
        file_url = media_data.get("url")
        if not file_url:
            print(f"❌ Impossible de récupérer l'URL du média {media_id}")
            return None
        
        file_response = requests.get(file_url, headers=headers)
        file_response.raise_for_status()
        
        # Sauvegarder avec le file_manager
        file_path = file_manager.save_file(
            content=file_response.content,
            filename=filename,
            source='whatsapp',
            original_filename=filename
        )
        
        print(f"✅ Média téléchargé: {filename}")
        return file_path
    
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement du média: {e}")
        return None


def process_whatsapp_message(message_data):
    """Traite un message WhatsApp et l'envoie à l'API FastAPI."""
    sender = None
    attachments_count = 0
    
    try:
        # Extraire les informations du message
        message_type = message_data.get("type")
        sender = message_data.get("from")
        timestamp = datetime.fromtimestamp(int(message_data.get("timestamp", 0))).isoformat()
        
        content_text = ""
        attachments = []
        metadata = {
            "whatsapp_message_id": message_data.get("id"),
            "message_type": message_type
        }
        
        # Traiter selon le type de message
        if message_type == "text":
            content_text = message_data.get("text", {}).get("body", "")
        
        elif message_type == "image":
            image_data = message_data.get("image", {})
            media_id = image_data.get("id")
            caption = image_data.get("caption", "")
            content_text = f"[Image] {caption}"
            
            if media_id:
                filename = f"whatsapp_image_{media_id}.jpg"
                file_path = download_whatsapp_media(media_id, filename)
                if file_path:
                    attachments.append(file_path)
        
        elif message_type == "document":
            doc_data = message_data.get("document", {})
            media_id = doc_data.get("id")
            filename = doc_data.get("filename", f"document_{media_id}")
            caption = doc_data.get("caption", "")
            content_text = f"[Document: {filename}] {caption}"
            
            if media_id:
                file_path = download_whatsapp_media(media_id, filename)
                if file_path:
                    attachments.append(file_path)
        
        elif message_type == "audio":
            audio_data = message_data.get("audio", {})
            media_id = audio_data.get("id")
            content_text = "[Message audio]"
            
            if media_id:
                filename = f"whatsapp_audio_{media_id}.ogg"
                file_path = download_whatsapp_media(media_id, filename)
                if file_path:
                    attachments.append(file_path)
        
        elif message_type == "video":
            video_data = message_data.get("video", {})
            media_id = video_data.get("id")
            caption = video_data.get("caption", "")
            content_text = f"[Vidéo] {caption}"
            
            if media_id:
                filename = f"whatsapp_video_{media_id}.mp4"
                file_path = download_whatsapp_media(media_id, filename)
                if file_path:
                    attachments.append(file_path)
        
        # Préparer le JSON pour l'API
        message_json = {
            "source": "whatsapp",
            "sender": sender,
            "client_id": None,  # À déterminer selon votre logique métier
            "timestamp": timestamp,
            "subject": None,
            "content_text": content_text,
            "attachments": attachments,
            "metadata": metadata,
            "status": "raw"
        }
        
        # Envoyer à l'API FastAPI
        try:
            api_start = time.time()
            response = requests.post(API_URL, json=message_json)
            response.raise_for_status()
            api_time = (time.time() - api_start) * 1000
            
            print(f"✅ Message WhatsApp envoyé avec succès de {sender}")
            print(f"   Réponse: {response.json()}")
            
            # Logger le succès
            attachments_count = len(attachments)
            message_logger.log_message(
                source='whatsapp',
                sender=sender,
                status='success',
                attachments_count=attachments_count
            )
            message_logger.log_api_call('/messages/', response.status_code, api_time)
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de l'envoi à l'API: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Détails: {e.response.text}")
            
            # Logger l'erreur
            message_logger.log_message(
                source='whatsapp',
                sender=sender,
                status='error',
                attachments_count=attachments_count,
                error_msg=str(e)
            )
            return False
    
    except Exception as e:
        print(f"❌ Erreur lors du traitement du message WhatsApp: {e}")
        message_logger.log_error('whatsapp', 'processing_error', str(e), sender=sender or 'unknown')
        return False


def handle_webhook(webhook_data):
    """
    Traite les données reçues via webhook WhatsApp.
    Cette fonction doit être appelée par votre serveur webhook.
    """
    try:
        # Vérifier la structure du webhook
        if "entry" not in webhook_data:
            print("❌ Format de webhook invalide")
            return False
        
        for entry in webhook_data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                for message in messages:
                    process_whatsapp_message(message)
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors du traitement du webhook: {e}")
        return False


# Exemple de données de test (simulant un webhook)
def test_with_sample_data():
    """Fonction de test avec des données simulées."""
    sample_webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "212600000000",
                        "id": "wamid.test123",
                        "timestamp": str(int(datetime.now().timestamp())),
                        "type": "text",
                        "text": {
                            "body": "Bonjour, je souhaite obtenir un crédit de 50000 MAD"
                        }
                    }]
                }
            }]
        }]
    }
    
    print("🔄 Test avec des données simulées...")
    handle_webhook(sample_webhook)


if __name__ == "__main__":
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("⚠️  WHATSAPP_ACCESS_TOKEN et WHATSAPP_PHONE_NUMBER_ID doivent être configurés dans .env")
        print("🔄 Exécution en mode test avec des données simulées...")
        test_with_sample_data()
    else:
        print("✅ Configuration WhatsApp détectée")
        print("💡 Ce script doit être intégré à votre serveur webhook")
        print("💡 Utilisez handle_webhook(data) dans votre endpoint webhook")

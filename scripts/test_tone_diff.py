import os
import sys
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_processor import EmailProcessor

def run_test(text):
    processor = EmailProcessor()
    mock_email = {
        "subject": "Test",
        "sender": "test@example.com",
        "content_text": text,
        "metadata": {"message_id": "test_id"}
    }
    results = processor.process_email_data(mock_email)
    sim = results.get('similarity_results', {})
    tone = sim.get('tone_estimation', {})
    return tone

text1 = "Je suis très en colère et j'ai besoin d'une réponse immédiate ! Mon dossier est bloqué depuis des mois !"
text2 = "Bonjour, je voudrais juste me renseigner sur vos tarifs pour un prêt immobilier. Je ne suis pas pressé."

tone1 = run_test(text1)
tone2 = run_test(text2)

print(f"Text 1 Tone: {tone1}")
print(f"Text 2 Tone: {tone2}")

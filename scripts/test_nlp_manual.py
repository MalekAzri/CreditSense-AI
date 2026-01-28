import sys
import os

# Add local directory to path so we can import process_messages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from process_messages import extract_key_info, advanced_clean

samples = [
    {
        "text": "Bonjour, je voudrais acheter une bagnole sport. J'ai besoin de 45000 dt.",
        "expected_type": "auto",
        "expected_amount": 45000.0
    },
    {
        "text": "Salut, projet de construction de villa. Le coût estimé est de 300 MD.",
        "expected_type": "immobilier",
        "expected_amount": 300000.0
    },
    {
        "text": "Je suis Ahmed Salah, mon numéro est 22334455 et mon CIN est 07654321.",
        "expected_name": "Ahmed Salah",
        "expected_phone": "22334455",
        "expected_cin": "07654321"
    },
    {
        "text": "Urgent, besoin d'argent pour un mariage. somme 10k dinars.",
        "expected_type": "consommation",
        "expected_amount": 10000.0
    }
]

print("🔍 Démarrage des tests NLP...\n")

for i, s in enumerate(samples):
    print(f"--- Test {i+1} ---")
    print(f"Input: {s['text']}")
    
    clean = advanced_clean("Sujet Test", s['text'])
    res = extract_key_info(clean)
    
    print(f"Extracted Type: {res['credit_type']} (Attendu: {s.get('expected_type')})")
    print(f"Extracted Amount: {res['amount']} (Attendu: {s.get('expected_amount')})")
    print(f"Extracted Client: {res['client_info']}")
    print("")

print("✅ Fin des tests.")

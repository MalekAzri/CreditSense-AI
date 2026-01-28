import logging
import sys
from pymongo import MongoClient

# Ensure we can import from local scripts
sys.path.append('.')
from scripts.process_messages import advanced_clean, extract_key_info, get_db

logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_phase2():
    print("🚀 Starting Verified Test for Phase 2 (Clean + Extract + NLP)\n")
    
    db = get_db()
    collection = db.messages
    
    # 1. Setup Test Data
    print("Step 1: Inserting Test Data into MongoDB...")
    collection.delete_many({}) # Clear DB for test
    
    test_cases = [
        {
            "subject": "Demande Crédit Auto",
            "body": "Bonjour,\nJe voudrais acheter une Toyota Yaris. J'ai besoin de 40 000 dt.\nMon téléphone est le 55123456.\nJe m'appelle Jean Pierre.",
            "attachments": ["/path/to/invoice.pdf"],
            "expectations": {
                "amount": 40000.0,
                "credit_type": "auto",
                "phone": "55123456",
                "name": "Jean Pierre",
                "attachments_count": 1
            }
        },
        {
            "subject": "Projet Immobilier",
            "body": "Besoin de financement pour une villa à Sousse. Budget: 350 MDT. CIN 08888888.\nDate limite: 15/03/2026.",
            "attachments": [],
            "expectations": {
                "amount": 350000.0,
                "credit_type": "immobilier",
                "cin": "08888888",
                "dates_count": 1
            }
        },
        {
            "subject": "Dossier PRO",
            "body": "Bonjour, dossier n° REF-2024-AB. Ci-joint ma fiche de paie.",
            "attachments": ["/path/to/paie.png"],
            "expectations": {
                "reference": "REF-2024-AB",
                "documents_mentioned": ["fiche de paie"],
                "attachments_count": 1
            }
        }
    ]
    
    for tc in test_cases:
        doc = {
            "source": "email_test",
            "sender": "test@example.com",
            "subject": tc["subject"],
            "body": tc["body"],
            "attachments": tc["attachments"],
            "status": "raw"
        }
        collection.insert_one(doc)
        
    print(f"✅ Inserted {len(test_cases)} documents.\n")
    
    # 2. Run Logic
    print("Step 2: Running Cleaning & Extraction Logic...")
    
    # Simulate the main loop
    processed_count = 0
    raw_msgs = collection.find({"status": "raw"})
    
    results = []
    
    for msg in raw_msgs:
        # Phase 2.1
        clean_val = advanced_clean(msg.get('subject', ''), msg.get('body', ''))
        
        # Phase 2.2
        extracted_data = extract_key_info(clean_val, msg.get('attachments', []))
        
        # Save results for verification
        results.append({
            "original_subject": msg['subject'],
            "extracted": extracted_data,
            "expectations": test_cases[processed_count]["expectations"]
        })
        
        # Update DB (as the real script would)
        collection.update_one(
            {"_id": msg["_id"]},
            {
                "$set": {
                    "clean_text": clean_val,
                    "extracted_data": extracted_data,
                    "status": "processed_phase2"
                }
            }
        )
        processed_count += 1
        
    print(f"✅ Processed {processed_count} documents.\n")
    
    with open("test_report.txt", "w", encoding="utf-8") as f:
        f.write("Step 3: Verification Report\n")
        f.write("="*60 + "\n")
        
        success_count = 0
        
        for i, res in enumerate(results):
            f.write(f"📧 Msg {i+1}: {res['original_subject']}\n")
            ext = res['extracted']
            exp = res['expectations']
            
            f.write(f"   Extracted Client Info: {ext['client_info']}\n")
            f.write(f"   Extracted Reference:   {ext['reference']}\n")
            f.write(f"   Extracted Amount:      {ext['amount']} {ext['currency']}\n")
            f.write(f"   Attachments:           {len(ext['attachments'])}\n")
            
            passed = True
            
            # Amount
            if "amount" in exp and ext['amount'] != exp['amount']:
               f.write(f"   ❌ Amount mismatch! Expected {exp['amount']}, got {ext['amount']}\n")
               passed = False

            # Type
            if "credit_type" in exp and ext['credit_type'] != exp['credit_type']:
               f.write(f"   ❌ Type mismatch! Expected {exp['credit_type']}, got {ext['credit_type']}\n")
               passed = False
               
            # CIN
            if "cin" in exp and ext['client_info']['cin'] != exp['cin']:
               f.write(f"   ❌ CIN mismatch! Expected {exp['cin']}, got {ext['client_info']['cin']}\n")
               passed = False
               
            # Phone
            if "phone" in exp and ext['client_info']['phone'] != exp['phone']:
                f.write(f"   ❌ Phone mismatch! Expected {exp['phone']}, got {ext['client_info']['phone']}\n")
                passed = False
                
            # Name
            # Check partial match because NER logic title cases it
            if "name" in exp:
                if not ext['client_info']['name'] or exp['name'] not in ext['client_info']['name']:
                    f.write(f"   ❌ Name mismatch! Expected {exp['name']}, got {ext['client_info']['name']}\n")
                    passed = False
                    
            # Ref
            if "reference" in exp and ext['reference'] != exp['reference']:
                f.write(f"   ❌ Ref mismatch! Expected {exp['reference']}, got {ext['reference']}\n")
                passed = False
                
            # Attachments Count
            if "attachments_count" in exp and len(ext['attachments']) != exp['attachments_count']:
                f.write(f"   ❌ Attachments mismatch! Expected {exp['attachments_count']}, got {len(ext['attachments'])}\n")
                passed = False
                
            # Docs mentioned
            if "documents_mentioned" in exp:
                for d in exp['documents_mentioned']:
                    if d not in ext['documents_mentioned']:
                        f.write(f"   ❌ Missing doc mention: {d}\n")
                        passed = False
                        
            # Dates count
            if "dates_count" in exp and len(ext['dates']) != exp['dates_count']:
                 f.write(f"   ❌ Dates count mismatch! Expected {exp['dates_count']}, got {len(ext['dates'])}\n")
                 passed = False

            if passed:
                f.write("   ✅ VERIFIED\n")
                success_count += 1
            else:
                f.write("   ⚠️ FAILED\n")
                
            f.write("-" * 60 + "\n")

        f.write(f"\nFinal Result: {success_count}/{len(test_cases)} tests passed.\n")
        print(f"Report written to test_report.txt. Success: {success_count}/{len(test_cases)}")

if __name__ == "__main__":
    test_phase2()

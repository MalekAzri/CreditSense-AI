import os
import re
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import spacy
from spacy.tokens import Doc

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load env vars
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "credit_platform")

# Load NLP Model
try:
    # Use large model for vectors and better NER
    logging.info("Loading spaCy model 'fr_core_news_lg'...")
    nlp = spacy.load("fr_core_news_lg")
    logging.info("Model loaded successfully.")
except OSError:
    logging.warning("Model 'fr_core_news_lg' not found. It is recommended for better results.")
    try:
        logging.info("Falling back to 'fr_core_news_sm'...")
        nlp = spacy.load("fr_core_news_sm")
    except OSError:
        logging.error("No spaCy model found. Please run: python -m spacy download fr_core_news_lg")
        raise

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def advanced_clean(subject, body):
    """
    Cleans email subject and body:
    - Combines them
    - Removes HTML
    - Removes signatures and reply blocks
    - Normalizes whitespace
    - KEEPS CASE for NER!
    """
    full_text = f"{subject or ''} . {body or ''}"
    
    # 1. Remove HTML
    try:
        soup = BeautifulSoup(full_text, "lxml")
    except Exception:
        soup = BeautifulSoup(full_text, "html.parser")
        
    text = soup.get_text(separator="\n")
    
    lines = text.split('\n')
    cleaned_lines = []
    
    stop_patterns = [
        r'^\s*cordialement',
        r'^\s*bien à vous',
        r'^\s*best regards',
        r'^\s*kind regards',
        r'^\s*sincerely',
        r'^\s*sent from my iphone',
        r'^\s*envoyé de mon iphone',
        r'^\s*envoyé depuis mon',
        r'^Le .+? a écrit\s*:',
        r'^On .+? wrote:',
        r'^-{2,}', # matches -- or ----------
        r'^_{2,}'  # matches __ or __________
    ]
    
    regexes = [re.compile(p, re.IGNORECASE) for p in stop_patterns]
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Check if line matches a stop pattern
        stop_found = False
        for p in regexes:
            if p.match(line_stripped):
                stop_found = True
                break
        
        if stop_found:
            break 
            
        if line_stripped.startswith('>'):
            continue
            
        cleaned_lines.append(line_stripped)
        
    # Join and normalize
    result = " ".join(cleaned_lines)
    result = re.sub(r'\s+', ' ', result).strip()
    
    # Fix punctuation spacing: "text ." -> "text."
    result = re.sub(r'\s+([.,!?])', r'\1', result)
    
    return result

def extract_credit_type_nlp(doc):
    """
    Uses semantic similarity to determine credit type.
    """
    if not nlp.has_pipe("tok2vec"):
        # If using small model without vectors, fallback to keywords?
        # But we assume large model here or handle gracefully.
        return extract_credit_type_keywords(doc.text)

    categories = {
        "immobilier": nlp("immobilier maison appartement terrain construction achat"),
        "auto": nlp("voiture auto véhicule moto bmw mercedes audi"),
        "consommation": nlp("consommation voyage mariage vacances argent personnel"),
        "professionnel": nlp("professionnel entreprise société matériel équipement projet"),
        "rachat": nlp("rachat crédit regroupement dette")
    }
    
    best_score = 0
    best_type = None
    
    # We compare the whole doc, or maybe just noun chunks?
    # Whole doc is easier but might be noisy. Let's try whole doc first.
    
    for cat_name, cat_doc in categories.items():
        score = doc.similarity(cat_doc)
        if score > best_score:
            best_score = score
            best_type = cat_name
            
    # Threshold to avoid random assignments
    if best_score < 0.3:
        return None
        
    return best_type
    
def extract_credit_type_keywords(text):
    """Fallback keyword extraction"""
    text_lower = text.lower()
    types = {
        "immobilier": ["immo", "maison", "appart", "villa", "terrain", "construction"],
        "auto": ["auto", "voiture", "moto", "véhicule"],
        "consommation": ["conso", "personnel", "projet", "voyage", "mariage"],
        "professionnel": ["pro", "entreprise", "materiel", "équipement", "société"],
        "rachat": ["rachat", "regroupement"]
    }
    for c_type, keywords in types.items():
        for k in keywords:
            if k in text_lower:
                return c_type
    return None

def extract_amount_nlp(doc):
    """
    Extracts amount looking for MONEY entities or numbers near 'montant'/'crédit'.
    """
    amounts = []
    
    # Strategy 1: Look for explicit currency symbols in text (Regex is still king for format)
    # But use NLP to validate context.
    text_lower = doc.text.lower()
    
    # Regex for Amount candidates
    regex_candidates = re.finditer(r'(\d+(?:[\s\.,]\d+)*)\s*(k|€|eur|dt|dinar|mill|mdt|md)?', text_lower)
    
    best_amount = None
    best_score = 0
    
    keywords_context = ["montant", "somme", "crédit", "emprunter", "besoin", "demande"]
    
    for match in regex_candidates:
        val_str = match.group(0)
        start, end = match.span()
        
        # Check if it's likely a phone number (start with 2/4/5/9 and long)
        clean_digits = re.sub(r'[^\d]', '', match.group(1))
        if len(clean_digits) == 8 and clean_digits[0] in ['2','4','5','9']:
            continue # Skip phone numbers
            
        # Context score: how close is this number to a keyword?
        # Find token corresponding to this match
        # (Approximate mapping)
        
        # Simple proximity check
        window_size = 50 
        window_start = max(0, start - window_size)
        window_end = min(len(text_lower), end + window_size)
        context_snippet = text_lower[window_start:window_end]
        
        score = 0
        for k in keywords_context:
            if k in context_snippet:
                score += 1
                
        # Bonus for currency suffix
        suffix = match.group(2)
        multiplier = 1
        currency = "DT"
        
        if suffix:
            score += 2 # Strong signal
            if suffix in ['k', 'mill', 'mdt', 'md']:
                multiplier = 1000
            elif suffix in ['€', 'eur']:
                currency = "EUR"
        
        try:
            val = float(match.group(1).replace(' ', '').replace(',', '.'))
            val = val * multiplier
            
            # Sanity check (Credit usually > 1000 unless consumption)
            if val < 100:
                score -= 1 
                
            if score > best_score:
                best_score = score
                best_amount = {"amount": val, "currency": currency}
                
        except ValueError:
            continue
            
    return best_amount

def extract_key_info(text, attachments=None):
    """
    Extracts information using comprehensive NLP pipeline.
    """
    if attachments is None:
        attachments = []
        
    data = {
        "amount": None,
        "currency": None,
        "credit_type": None,
        "client_info": {
            "name": None,
            "cin": None,
            "phone": None,
            "email": None
        },
        "reference": None,
        "dates": [],
        "documents_mentioned": [],
        "attachments": attachments
    }
    
    # Run NLP on clean text (Case Preserved)
    doc = nlp(text) 
    
    # 1. Credit Type (Similarity)
    data["credit_type"] = extract_credit_type_nlp(doc)
    
    # 2. Amount (Contextual Regex)
    amt_obj = extract_amount_nlp(doc)
    if amt_obj:
        data["amount"] = amt_obj["amount"]
        data["currency"] = amt_obj["currency"]

    # 3. Client Info
    
    # A. Name (NER)
    for ent in doc.ents:
        if ent.label_ == "PER":
            # Heuristic: Name is usually 2+ words
            if len(ent.text.split()) >= 2:
                # Avoid "Monsieur", "Madame" as name
                clean_name = ent.text.replace("Monsieur", "").replace("Madame", "").strip()
                if len(clean_name) > 3:
                    data["client_info"]["name"] = clean_name.title()
                    break # Take first person found (usually sender)
    
    # B. Phone & CIN (Regex is better for fixed formats)
    text_lower = text.lower()
    
    # Phone
    phone_match = re.search(r'\b([2459]\d{7})\b', text_lower)
    if phone_match:
         data["client_info"]["phone"] = phone_match.group(1)
         
    # CIN (8 digits, not the phone)
    cin_matches = re.finditer(r'\b(\d{8})\b', text_lower)
    for m in cin_matches:
        candidate = m.group(1)
        if data["client_info"]["phone"] == candidate:
            continue
        data["client_info"]["cin"] = candidate
        break
        
    # Email
    email_match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text_lower)
    if email_match:
        data["client_info"]["email"] = email_match.group(0) 
        
    # 4. Reference
    ref_match = re.search(r'(dossier|ref|réf|numéro|n°)\s*[:\.]?\s*([a-z0-9\-\/]*\d[a-z0-9\-\/]*)', text_lower)
    if ref_match:
        data["reference"] = ref_match.group(2).upper()
        
    # 5. Documents Mentioned
    doc_keywords = ["cin", "fiche de paie", "relevé", "bancaire", "titre", "devis", "facture", "passeport"]
    for d in doc_keywords:
        if d in text_lower:
            data["documents_mentioned"].append(d)
            
    return data

def main():
    db = get_db()
    # Process both 'raw' and 'training_data' (synthetic) messages
    messages = db.messages.find({"status": {"$in": ["raw", "training_data"]}})
    
    count = 0
    logging.info("Starting NLP processing...")
    
    for msg in messages:
        original_subject = msg.get('subject', '')
        original_body = msg.get('content_text', '') # Changed from 'body' to 'content_text' as per schema
        attachments = msg.get('attachments', [])
        
        # 1. Cleaning
        clean_text = advanced_clean(original_subject, original_body)
        
        # 2. NLP Extraction
        extracted_data = extract_key_info(clean_text, attachments)
        
        logging.info(f"Processing Msg ID {msg['_id']}")
        logging.info(f"  Extracted: {extracted_data}")
        
        # 3. Update DB
        db.messages.update_one(
            {"_id": msg["_id"]},
            {
                "$set": {
                    "clean_text": clean_text,
                    "extracted_data": extracted_data,
                    "status": "processed" 
                }
            }
        )
        count += 1
        
    logging.info(f"Phase 2 NLP Complete. Processed {count} messages.")

if __name__ == "__main__":
    main()

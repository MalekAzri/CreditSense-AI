import os
import sys
import re
import logging
from bs4 import BeautifulSoup
import spacy
from pymongo import MongoClient
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import statistics
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
# Ensure encoding is handled or just avoid special chars. 
# Actually, the error was in print() in main.py. Logging module usually handles it better or errors inside it.
# Let's verify EmailProcessor usage of emojis.

class EmailProcessor:
    def __init__(self):
        # 1. Load Config
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "creditapp")
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.qdrant_collection = "synthetic_emails"
        self.vector_collection = "email_vectors"
        self.model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        self.k_neighbors = 5
        self.user_email = os.getenv("USER_EMAIL", "")

        # 2. Initialize Clients
        self.mongo_client = MongoClient(self.mongo_uri)
        self.db = self.mongo_client[self.db_name]
        
        if self.qdrant_url and self.qdrant_api_key:
            self.qdrant = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
        else:
            logging.error("Qdrant credentials missing!")
            self.qdrant = None

        # 3. Load Models
        logging.info("Loading models...")
        try:
            self.nlp = spacy.load("fr_core_news_lg")
        except:
            self.nlp = spacy.load("fr_core_news_sm")
            
        self.embedder = SentenceTransformer(self.model_name)
        logging.info("Models loaded.")

    def process_single_email(self, email_id: str) -> dict:
        logging.info(f"[START] Processing email {email_id}...")
        
        # 1. Fetch Email
        from bson import ObjectId
        try:
            doc = self.db.messages.find_one({"_id": ObjectId(email_id)})
        except:
            doc = self.db.messages.find_one({"_id": email_id})
            
        if not doc:
            logging.error(f"Email {email_id} not found.")
            return {"error": "not found"}

        # 2. Clean Text
        clean_text = self._advanced_clean(doc.get("subject"), doc.get("content_text") or doc.get("body"))
        
        # 3. Extract NLP Data (Optional but good for 'processed' status)
        extracted_data = self._extract_key_info(clean_text)
        
        # Update Mongo with Clean Data
        self.db.messages.update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "clean_text": clean_text,
                "extracted_data": extracted_data,
                "status": "processed",
                "processed_at": datetime.now()
            }}
        )

        # 4. Check Direction (Sent vs Received)
        sender = doc.get("sender", "")
        if self._is_sent_email(sender):
            logging.info(f"[SKIP] Email {email_id} is SENT. Stopping pipeline.")
            self.db.messages.update_one(
                {"_id": doc["_id"]},
                {"$set": {"vectorized": True, "vectorization_status": "skipped_sent"}}
            )
            return {"status": "skipped_sent"}

        # 5. Vectorize
        vector = self.embedder.encode(clean_text).tolist()
        
        # Update Mongo (Vectorized)
        self.db.messages.update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "vectorized": True, 
                "vectorized_at": datetime.now()
            }}
        )
        
        # Upsert to Qdrant (Optional for received emails, good for history)
        # We skip upserting to 'email_vectors' for simplicity in this realtime flow unless specifically requested, 
        # but the plan said to upsert. Let's do it if easy.
        # Requires PointStruct.
        try:
            from qdrant_client.models import PointStruct
            import uuid
            point_id = str(uuid.uuid4())
            self.qdrant.upsert(
                collection_name=self.vector_collection,
                points=[PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "mongo_id": str(doc["_id"]),
                        "subject": doc.get("subject"),
                        "clean_text_preview": clean_text[:200],
                        "direction": "received"
                    }
                )]
            )
        except Exception as e:
            logging.warning(f"Failed to upsert to Qdrant history: {e}")

        # 6. Similarity Search
        sim_results = self._analyze_similarity(vector)
        
        # 7. Update Mongo (Final)
        self.db.messages.update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "similarity_results": sim_results,
                "analysis_completed_at": datetime.now()
            }}
        )
        
        logging.info(f"[SUCCESS] Email {email_id} fully processed. Intent: {sim_results.get('top_intent')}")
        return {
            "status": "success", 
            "sender": sender,
            "clean_text": clean_text,
            "extracted_data": extracted_data,
            "similarity": sim_results
        }

    def _advanced_clean(self, subject, body):
        full_text = f"{subject or ''} . {body or ''}"
        
        # 1. Remove HTML
        try:
            soup = BeautifulSoup(full_text, "lxml")
        except:
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
            r'^-{2,}', 
            r'^_{2,}'  
        ]
        
        regexes = [re.compile(p, re.IGNORECASE) for p in stop_patterns]
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped: continue
                
            stop_found = False
            for p in regexes:
                if p.match(line_stripped):
                    stop_found = True
                    break
            
            if stop_found: break 
                
            if line_stripped.startswith('>'): continue
                
            cleaned_lines.append(line_stripped)
            
        result = " ".join(cleaned_lines)
        result = re.sub(r'\s+', ' ', result).strip()
        result = re.sub(r'\s+([.,!?])', r'\1', result)
        
        return result

    def _extract_key_info(self, text, attachments=None):
        if attachments is None: attachments = []
        
        data = {
            "amount": None,
            "currency": None,
            "credit_type": None,
            "client_info": {"name": None, "cin": None, "phone": None, "email": None},
            "reference": None,
            "documents_mentioned": [],
            "attachments": attachments
        }
        
        doc = self.nlp(text)
        
        # 1. Credit Type
        data["credit_type"] = self._extract_credit_type(doc, text)
        
        # 2. Amount
        amt_obj = self._extract_amount(text)
        if amt_obj:
            data["amount"] = amt_obj["amount"]
            data["currency"] = amt_obj["currency"]
            
        # 3. Client Info
        # Name Extraction (Hybrid: NER + Pattern Matching for "Je suis...")
        # Try Regex specific patterns first (often more reliable in informal emails)
        # Regex explanation:
        # (?:...) : Non-capturing group for prefix
        # \s+ : Spaces
        # ([a-zA-Z\s]{3,20}?) : Capture group, lazy match to avoid eating into next field
        # (?=\s+(?:mon|ma|je|j'|cin|tel|tél|email|mail)|$|[.,:;]) : Lookahead to stop at keywords or punctuation
        
        name_patterns = [
            r"(?:je suis|je m'appelle|c'est|nom est|prenom est)\s+([a-zA-Z\s]{3,20}?)(?=\s+(?:mon|ma|je|j'|cin|tel|tél|email|mail)|$|[.,:;])",
            r"nom\s*:\s*([a-zA-Z\s]{3,20}?)(?=\s+(?:prenom|cin|tel)|$|[.,:;])"
        ]
        for pat in name_patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # Validate candidate (not a common stopword)
                if len(candidate.split()) >= 2 and len(candidate) > 3:
                     data["client_info"]["name"] = candidate.title()
                     break

        # Fallback to NER if no regex match
        if not data["client_info"]["name"]:
            for ent in doc.ents:
                if ent.label_ == "PER":
                    if len(ent.text.split()) >= 2:
                        clean_name = ent.text.replace("Monsieur", "").replace("Madame", "").strip()
                        if len(clean_name) > 3:
                            data["client_info"]["name"] = clean_name.title()
                            break
        
        # Regex for Phone, CIN, Email
        text_lower = text.lower()
        
        # Priority 1: Explicit Key-Value matches (e.g., "cin: 12345678", "tel 55555555")
        # These are very strong signals, so we check them first.
        
        # CIN Pattern: keyword + optional separator + 8 digits
        cin_explicit = re.search(r"(?:cin|nid|carte|identit[é|e])\D{0,10}?(\d{8})\b", text_lower)
        if cin_explicit:
            data["client_info"]["cin"] = cin_explicit.group(1)
            
        # Phone Pattern: keyword + optional separator + 8 digits
        phone_explicit = re.search(r"(?:tel|tél|phone|gsm|mobile|contact|appel)\D{0,10}?(\d{8})\b", text_lower)
        if phone_explicit:
            data["client_info"]["phone"] = phone_explicit.group(1)
            
        # Priority 2: General search (if specific fields missing)
        # Helper to check context
        def has_context(full_text, start, end, keywords, window=20):
            snippet = full_text[max(0, start-window):min(len(full_text), end+window)]
            return any(k in snippet for k in keywords)

        # Config regex
        # CIN: 8 digits
        # Phone: 8 digits, starts with 2,4,5,9 (Tunisie)
        
        if not data["client_info"]["cin"] or not data["client_info"]["phone"]:
            potential_numbers = list(re.finditer(r'\b(\d{8})\b', text_lower))
            
            phone_keywords = ["tel", "tél", "phone", "mobile", "gsm", "contact", "appeler"]
            cin_keywords = ["cin", "carte", "identit", "nid", "n°"]

            for m in potential_numbers:
                val = m.group(1)
                # Skip if already captured
                if val == data["client_info"]["cin"] or val == data["client_info"]["phone"]:
                    continue
                    
                start, end = m.span()
                
                # Context checks
                is_cin_context = has_context(text_lower, start, end, cin_keywords)
                is_phone_context = has_context(text_lower, start, end, phone_keywords)
                
                # Decision logic
                if is_cin_context and not data["client_info"]["cin"]:
                    data["client_info"]["cin"] = val
                elif is_phone_context and not data["client_info"]["phone"]:
                    data["client_info"]["phone"] = val
                else:
                    # Default behavior based on digit structure (Fallback)
                    if val[0] in ['2','4','5','9']:
                        if not data["client_info"]["phone"]: data["client_info"]["phone"] = val
                    else:
                        if not data["client_info"]["cin"]: data["client_info"]["cin"] = val

        # Handle specific case where user said "mon cin:55555555" (starts with 5, could be phone regex match)
        # The loop above handles it via context.
            
        email_match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text_lower)
        if email_match: data["client_info"]["email"] = email_match.group(0)
            
        # 4. Reference
        ref_match = re.search(r'(dossier|ref|réf|numéro|n°)\s*[:\.]?\s*([a-z0-9\-\/]*\d[a-z0-9\-\/]*)', text_lower)
        if ref_match: data["reference"] = ref_match.group(2).upper()
            
        # 5. Documents
        doc_keywords = ["cin", "fiche de paie", "relevé", "bancaire", "titre", "devis", "facture", "passeport"]
        for d in doc_keywords:
            if d in text_lower: data["documents_mentioned"].append(d)
                
        return data

    def _extract_credit_type(self, doc, text):
        # 1. Direct Keyword Matching (Reliable)
        text_lower = text.lower()
        if "immobilier" in text_lower or "maison" in text_lower or "appart" in text_lower:
            return "immobilier"
        if "voiture" in text_lower or "auto" in text_lower or "véhicule" in text_lower:
            return "auto"
        if "consommation" in text_lower or "conso" in text_lower or "personnel" in text_lower:
            return "consommation"
        if "travaux" in text_lower or "amenagement" in text_lower:
             return "travaux"
        
        # 2. Vector Similarity (Fallback)
        categories = {
            "immobilier": self.nlp("immobilier maison appartement terrain construction achat"),
            "auto": self.nlp("voiture auto véhicule moto bmw mercedes audi"),
            "consommation": self.nlp("consommation voyage mariage vacances argent personnel"),
            "professionnel": self.nlp("professionnel entreprise société matériel équipement projet"),
            "rachat": self.nlp("rachat crédit regroupement dette")
        }
        best_score, best_type = 0, None
        for cat_name, cat_doc in categories.items():
            score = doc.similarity(cat_doc)
            if score > best_score:
                best_score, best_type = score, cat_name
        return best_type if best_score > 0.3 else None

    def _extract_amount(self, text):
        text_lower = text.lower()
        regex_candidates = re.finditer(r'(\d+(?:[\s\.,]\d+)*)\s*(k|€|eur|dt|dinar|mill|mdt|md)?', text_lower)
        best_amount, best_score = None, 0
        keywords_context = ["montant", "somme", "crédit", "emprunter", "besoin", "demande"]
        
        for match in regex_candidates:
            val_str = match.group(0)
            start, end = match.span()
            clean_digits = re.sub(r'[^\d]', '', match.group(1))
            if len(clean_digits) == 8 and clean_digits[0] in ['2','4','5','9']: continue
            
            # Proximity check
            window_size = 50 
            context_snippet = text_lower[max(0, start-window_size):min(len(text_lower), end+window_size)]
            score = sum(1 for k in keywords_context if k in context_snippet)
            
            suffix = match.group(2)
            multiplier, currency = 1, "DT"
            if suffix:
                score += 2
                if suffix in ['k', 'mill', 'mdt', 'md']: multiplier = 1000
                elif suffix in ['€', 'eur']: currency = "EUR"
            
            try:
                val = float(match.group(1).replace(' ', '').replace(',', '.')) * multiplier
                if val < 100: score -= 1 
                if score > best_score:
                    best_score = score
                    best_amount = {"amount": val, "currency": currency}
            except: continue
        return best_amount

    def _is_sent_email(self, sender):

        if not self.user_email:
            return False
        return self.user_email.lower() in sender.lower() if sender else False

    def _analyze_similarity(self, vector):
        if not self.qdrant: return {}
        
        try:
            search_result = self.qdrant.query_points(
                collection_name=self.qdrant_collection,
                query=vector,
                limit=self.k_neighbors,
                with_payload=True
            ).points
        except: 
            return {"error": "search failed"}

        if not search_result:
            return {"top_intent": "UNKNOWN", "confidence": 0.0}

        intents = [p.payload.get("intent") for p in search_result if p.payload.get("intent")]
        
        if intents:
            most_common = Counter(intents).most_common(1)
            top_intent = most_common[0][0]
            confidence = most_common[0][1] / len(intents)
        else:
            top_intent = "UNKNOWN"
            confidence = 0.0
            
        # Tone Aggregation (Average of neighbors)
        tone_scores = {"urgency": [], "stress": [], "seriousness": []}
        for p in search_result:
            tone = p.payload.get("tone", {})
            if isinstance(tone, dict):
                tone_scores["urgency"].append(tone.get("urgency", 0))
                tone_scores["stress"].append(tone.get("stress", 0))
                tone_scores["seriousness"].append(tone.get("seriousness", 0))
        
        avg_tone = {
            "urgency": round(statistics.mean(tone_scores["urgency"]), 2) if tone_scores["urgency"] else 0,
            "stress": round(statistics.mean(tone_scores["stress"]), 2) if tone_scores["stress"] else 0,
            "seriousness": round(statistics.mean(tone_scores["seriousness"]), 2) if tone_scores["seriousness"] else 0
        }
        
        return {
            "top_intent": top_intent, 
            "confidence": round(confidence, 2),
            "tone_estimation": avg_tone,
            "matched_examples": [p.id for p in search_result]
        }

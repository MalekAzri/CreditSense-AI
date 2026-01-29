import os
import joblib
import pandas as pd
from typing import Optional, List

class ReplyGenerator:
    def __init__(self):
        self.models_dir = "models"
        self.classifier_path = os.path.join(self.models_dir, "email_classifier.joblib")
        self.responses_path = os.path.join(self.models_dir, "responses.joblib")
        
        # Load models
        try:
            self.model = joblib.load(self.classifier_path)
            self.responses_template = joblib.load(self.responses_path)
        except Exception as e:
            print(f"[REPLY_GEN] Error loading models: {e}")
            self.model = None
            self.responses_template = {}

    def generate_auto_reply(self, email_text: str, client_data: Optional[dict] = None) -> str:
        """
        Generates a personalized reply based on intent and missing documents.
        """
        if not self.model:
            return "Bonjour, merci pour votre message. Un conseiller CreditSense va vous recontacter prochainement."

        # 1. Predict Intent
        intent = self.model.predict([email_text])[0]
        
        # 2. Get Base Template
        base_reply = self.responses_template.get(intent, self.responses_template.get("other"))

        # 3. Personalize if client data is available
        if client_data:
            name = client_data.get('nom', 'Client')
            type_client = client_data.get('typeClient', 'individu') # individu or pme
            
            # Logic for missing documents
            missing_docs = self._get_missing_documents(client_data, type_client)
            
            if intent == "document_request" or (intent == "status_request" and missing_docs):
                personalization = f"Bonjour {name},\n\n"
                if missing_docs:
                    docs_list = "\n- ".join(missing_docs)
                    personalization += f"Pour faire avancer l'étude de votre crédit, il nous manque encore les documents suivants :\n- {docs_list}\n\nMerci de nous les envoyer par retour d'email."
                else:
                    personalization += "Bonne nouvelle : votre dossier est complet ! Nous n'attendons plus aucune pièce de votre part."
                
                personalization += "\n\nCordialement,\nL'équipe CreditSense."
                return personalization

        # Fallback to standard template if no client info or other intent
        return base_reply

    def _get_missing_documents(self, client: dict, type_client: str) -> List[str]:
        """
        Calculates missing documents based on profile type.
        """
        missing = []
        
        if type_client.lower() == "pme":
            # PME Requirements
            docs_to_check = {
                "Registre de commerce": "doc_registre_commerce",
                "Matricule fiscal": "doc_matricule_fiscal",
                "Bilan": "doc_bilan",
                "Compte de résultat": "doc_compte_resultat",
                "Relevés bancaires": "doc_releves_bancaires",
                "Demande de crédit PME": "doc_demande_credit_pme",
                "CIN dirigeant": "doc_cin_dirigeant"
            }
        else:
            # Individual Requirements
            docs_to_check = {
                "Identité (CIN/Passeport)": "doc_identite",
                "Demande de crédit": "doc_demande_credit",
                "Bulletin bancaire": "doc_bulletin_bancaire",
                "Relevés bancaires": "doc_releves_bancaires",
                "Bilan (si indépendant)": "doc_bilan",
                "Domicile (Facture eau/élec)": "doc_facture_domicile"
            }

        for label, field in docs_to_check.items():
            val = client.get(field)
            if val is None or val == "" or str(val).lower() == "nan":
                # Special case for "Bilan" in Individual: only check if it's explicitly needed or just skip?
                # User said: "Bilan : (Uniquement si le client est indépendant)"
                # For now we include it as per user's "mettez tous ce documents"
                missing.append(label)
                
        return missing

import joblib
import pandas as pd
import re
import os

class CreditSenseAgent:
    def __init__(self):
        # Charger le modèle de classification
        self.model = joblib.load("models/email_classifier.joblib")
        self.responses_template = joblib.load("models/responses.joblib")
        # Charger la base client (modifiable par l'utilisateur)
        self.clients_db_path = "data/clients.csv"
        self.load_clients()

    def load_clients(self):
        if os.path.exists(self.clients_db_path):
            self.clients_df = pd.read_csv(self.clients_db_path)
        else:
            print("Erreur : Fichier clients.csv introuvable.")
            self.clients_df = pd.DataFrame()

    def extract_client_info(self, text):
        """Extrait l'email ou le numéro de dossier du texte."""
        # Chercher un email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        # Chercher un numéro de dossier type CS-xxx ou PME-xxx
        folder_match = re.search(r'(CS|PME)-\d+', text)
        
        return {
            "email": email_match.group(0) if email_match else None,
            "num_dossier": folder_match.group(0) if folder_match else None
        }

    def get_client_data(self, info):
        """Cherche le client dans le CSV."""
        if self.clients_df.empty:
            return None
        
        res = None
        if info['email']:
            res = self.clients_df[self.clients_df['email'] == info['email']]
        elif info['num_dossier']:
            res = self.clients_df[self.clients_df['num_dossier'] == info['num_dossier']]
        
        return res.iloc[0] if res is not None and not res.empty else None

    def get_missing_docs(self, client_data):
        """Identifie les documents manquants selon le type de client."""
        type_client = str(client_data.get('type_client', 'Individuel'))
        
        if type_client == "PME":
            required_docs = {
                "Registre de commerce": "registre_commerce",
                "Matricule fiscal": "matricule_fiscal",
                "Bilan": "bilan",
                "Compte de résultat": "compte_resultat",
                "Relevés bancaires": "releves_bancaires",
                "Demande de crédit PME": "demande_credit_pme",
                "CIN dirigeant": "cin_dirigeant"
            }
        else: # Individuel
            required_docs = {
                "Identité (CIN/Passeport)": "cin_passeport",
                "Demande de crédit": "demande_credit",
                "Bulletin bancaire": "bulletin_bancaire",
                "Relevés bancaires": "releves_bancaires",
                "Bilan (si indépendant)": "bilan",
                "Domicile (Facture eau/élec)": "facture_domicile"
            }

        missing = []
        for display_name, field in required_docs.items():
            val = str(client_data.get(field, "N/A")).strip()
            if val in ["N/A", "", "nan", "None"]:
                missing.append(display_name)
        
        return missing, type_client

    def process_email(self, email_text):
        # 1. Identifier l'intention via le modèle ML
        intent = self.model.predict([email_text])[0]
        
        # 2. Identifier le client
        client_info = self.extract_client_info(email_text)
        client_data = self.get_client_data(client_info)
        
        # 3. Construire la réponse personnalisée
        if client_data is not None:
            nom = client_data['nom']
            num_dossier = client_data['num_dossier']
            etat = client_data['etat_credit']
            missing_docs, type_c = self.get_missing_docs(client_data)
            
            # Message de base avec le statut
            response = f"Bonjour {nom},\n\nConcernant votre dossier {num_dossier} (Profil {type_c}), votre demande est actuellement : **{etat}**.\n\n"
            
            # Ajout des documents manquants si nécessaire
            if missing_docs:
                docs_list = "\n- ".join(missing_docs)
                response += f"Pour faire avancer l'étude de votre crédit, il nous manque encore les documents suivants :\n- {docs_list}\n\nMerci de nous les envoyer par retour d'email."
            else:
                response += "Bonne nouvelle : votre dossier est complet ! Nous n'attendons plus aucune pièce de votre part."
            
            response += "\n\nCordialement,\nL'équipe CreditSense."
            return response
        
        # Réponse par défaut si client non trouvé
        return self.responses_template.get(intent, "Bonjour, merci pour votre message. Un conseiller CreditSense va vous recontacter prochainement.")

if __name__ == "__main__":
    print("CreditSenseAgent chargé. Utilisez src/test_system.py pour lancer les tests.")

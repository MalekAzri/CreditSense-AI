import pandas as pd
import pickle
import os
import numpy as np

class CreditScorer:
    def __init__(self, model_path='models/credit_scoring_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.final_columns = None
        self.feature_importances = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.final_columns = data['columns']
                # Store feature importances for globally important features
                self.feature_importances = pd.Series(
                    self.model.feature_importances_, 
                    index=self.final_columns
                ).sort_values(ascending=False)
        else:
            print(f"[ERROR] Model file not found at {self.model_path}")

    def analyze_client(self, client_data):
        if self.model is None:
            return {"error": "Model not loaded"}

        # Mapping Prisma fields to ML features (German Credit Mapping)
        # This is a simplification, ideally we'd have a robust mapper
        processed_data = {
            'status_account': client_data.get('compte_courant', 'A14'), # A14: no checking account
            'duration': client_data.get('duree_mois', 12),
            'credit_history': client_data.get('historique_credit', 'A34'), # A34: critical account
            'purpose': client_data.get('objectif_credit', 'A43'), # A43: radio/television
            'credit_amount': client_data.get('montant_credit', 1000),
            'savings': 'A61', # < 100 DM default
            'employment': 'A73', # 1-4 years default
            'installment_rate': client_data.get('taux_remboursement', 2),
            'personal_status': client_data.get('statut_personnel', 'A93'),
            'other_debtors': 'A101',
            'residence_since': client_data.get('residence_depuis', 2),
            'property': 'A121',
            'age': client_data.get('age', 30),
            'other_installments': 'A143',
            'housing': client_data.get('logement', 'A152'),
            'existing_credits': client_data.get('nb_credits_banque', 1),
            'job': 'A173',
            'people_liable': client_data.get('personnes_a_charge', 1),
            'telephone': 'A191',
            'foreign_worker': 'A201' if client_data.get('travailleur_etranger', True) else 'A202'
        }

        # Predict
        client_df = pd.DataFrame([processed_data])
        client_encoded = pd.get_dummies(client_df)
        
        for col in self.final_columns:
            if col not in client_encoded.columns:
                client_encoded[col] = 0
        
        client_encoded = client_encoded[self.final_columns]
        client_scaled = self.scaler.transform(client_encoded)
        
        # Risk probability (proportion of trees voting for "Bad")
        risk_proba = self.model.predict_proba(client_scaled)[0, 1]
        
        # Risk Score (0-100)
        risk_score = risk_proba * 100
        reliability_score = (1 - risk_proba) * 100
        
        decision = "OUI" if reliability_score >= 50 else "NON"

        # Generate "Why" (Simplified Local Explanation)
        explanations = self._generate_explanation(processed_data, risk_score)

        return {
            "decision": decision,
            "risk_score": round(risk_score, 2),
            "reliability_score": round(reliability_score, 2),
            "reasons": explanations
        }

    def _generate_explanation(self, data, risk_score):
        reasons = []
        
        # Heuristic-based explanations for the German Credit Dataset context
        if risk_score > 50:
            if data['duration'] > 24:
                reasons.append("La durée du crédit est trop longue, augmentant l'incertitude.")
            if data['credit_amount'] > 5000:
                reasons.append("Le montant demandé est élevé par rapport au profil de risque.")
            if data['age'] < 25:
                reasons.append("L'âge de l'emprunteur est un facteur de risque (jeune emprunteur).")
            if data['status_account'] in ['A11', 'A12']:
                reasons.append("Le solde du compte courant est faible ou négatif.")
            if data['credit_history'] in ['A30', 'A31']:
                reasons.append("Des retards de paiement ont été détectés dans l'historique.")
        else:
            reasons.append("L'historique de crédit et la stabilité financière sont jugés satisfaisants.")
            if data['status_account'] == 'A14':
                reasons.append("L'absence d'historique de découvert bancaire est positive.")
            if data['age'] > 35:
                reasons.append("La maturité de l'emprunteur renforce la stabilité du dossier.")

        # Ensure we have at least something
        if not reasons:
            reasons.append("Analyse basée sur les variables de solvabilité standard du modèle.")
            
        return reasons[:3] # Return top 3 reasons

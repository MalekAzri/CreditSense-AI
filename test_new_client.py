import pandas as pd
import pickle

def calculer_score_credit(client_data, model, scaler, final_columns):
    """
    Fonction pour préparer les données d'un nouveau client et prédire son score.
    """
    # Création du DataFrame pour le client
    client_df = pd.DataFrame([client_data])
    
    # Encodage One-Hot (doit correspondre aux colonnes du modèle d'entraînement)
    client_encoded = pd.get_dummies(client_df)
    
    # Réalignement des colonnes (ajout des colonnes manquantes avec 0)
    for col in final_columns:
        if col not in client_encoded.columns:
            client_encoded[col] = 0
            
    # S'assurer de l'ordre exact des colonnes
    client_encoded = client_encoded[final_columns]
    
    # Normalisation
    client_scaled = scaler.transform(client_encoded)
    
    # Prédiction de la probabilité de risque
    proba_risque = model.predict_proba(client_scaled)[0, 1]
    
    # Calcul du score sur 100 (100 = excellent, 0 = très risqué)
    score = (1 - proba_risque) * 100
    decision = "ACCEPTÉ" if score >= 50 else "REFUSÉ"
    
    return score, decision, proba_risque

def main():
    # 1. Chargement du modèle sauvegardé
    print("Chargement du modèle...")
    try:
        with open('credit_scoring_model.pkl', 'rb') as f:
            data = pickle.load(f)
            model = data['model']
            scaler = data['scaler']
            final_columns = data['columns']
    except FileNotFoundError:
        print("Erreur : Le fichier 'credit_scoring_model.pkl' n'existe pas. Lancez d'abord credit_scoring.py.")
        return

    # 2. Définition d'une nouvelle ligne de données (Exemple de client)
    # Note: On utilise les noms de colonnes originaux avant encodage
    nouveau_client = {
        'status_account': 'A11',      # < 0 DM
        'duration': 24,               # 24 mois
        'credit_history': 'A32',      # Crédits existants remboursés
        'purpose': 'A43',             # Radio/TV
        'credit_amount': 4870,        # Montant
        'savings': 'A61',             # < 100 DM
        'employment': 'A73',          # Employé depuis 1-4 ans
        'installment_rate': 3,        # Taux d'endettement
        'personal_status': 'A93',     # Homme : célibataire
        'other_debtors': 'A101',      # Aucun
        'residence_since': 4,         # Depuis 4 ans
        'property': 'A121',           # Immobilier
        'age': 53,                    # Âge
        'other_installments': 'A143', # Aucun
        'housing': 'A153',            # Logement gratuit
        'existing_credits': 2,        # 2 crédits en cours
        'job': 'A173',                # Qualifié
        'people_liable': 1,           # 1 personne à charge
        'telephone': 'A191',          # Aucun
        'foreign_worker': 'A201'      # Oui
    }

    # 3. Calcul du score
    score, decision, proba = calculer_score_credit(nouveau_client, model, scaler, final_columns)

    # 4. Affichage du résultat
    print("\n" + "="*40)
    print("      RÉSULTAT DU CRÉDIT")
    print("="*40)
    print(f"Probabilité de risque : {proba:.2%}")
    print(f"Score de fiabilité    : {score:.1f} / 100")
    print(f"Décision finale       : {decision}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import os

def train_and_save_model():
    # 1. Charger les données
    data_path = "data/credit_emails.csv"
    if not os.path.exists(data_path):
        print(f"Erreur : Le fichier {data_path} n'existe pas. Lancez d'abord generate_dataset.py.")
        return

    df = pd.read_csv(data_path)
    X = df['text']
    y = df['label']

    # 2. Diviser les données (Train/Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Créer un pipeline (TF-IDF + Random Forest)
    # On utilise le Random Forest qui est robuste et performant
    model = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2))), # Unigrammes et Bigrammes pour capturer le contexte
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    # 4. Entraîner le modèle
    print("Entraînement du modèle en cours...")
    model.fit(X_train, y_train)

    # 5. Évaluer le modèle
    y_pred = model.predict(X_test)
    print("\nScore de performance :")
    print(classification_report(y_test, y_pred))

    # 6. Sauvegarder le modèle
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    model_path = os.path.join(models_dir, "email_classifier.joblib")
    joblib.dump(model, model_path)
    print(f"\nModèle sauvegardé avec succès dans : {model_path}")

    # 7. Définir les réponses types (Logique métier)
    responses = {
        "document_request": "Bonjour,\n\nPour traiter votre dossier, nous avons besoin de documents spécifiques selon votre profil :\n\n- Client Individuel :\n  * CIN / Passeport\n  * Demande de crédit\n  * Bulletin bancaire et Relevés bancaires\n  * Facture de domicile\n\n- Client PME :\n  * Registre de commerce et Matricule fiscal\n  * Bilan et Compte de résultat\n  * Relevés bancaires\n\nMerci de nous préciser votre numéro de dossier (CS-xxx ou PME-xxx) pour une réponse personnalisée.\n\nCordialement,\nService Crédit.",
        "status_request": "Bonjour,\n\nNous avons bien reçu votre demande de suivi. Pourriez-vous nous fournir votre numéro de dossier (ex: CS-001) afin que nous puissions vous donner l'état exact de votre demande ?\n\nCordialement,\nService Client.",
        "other": "Bonjour,\n\nMerci pour votre message. Nous avons bien pris en compte votre demande et un conseiller CreditSense reviendra vers vous dans les plus brefs délais.\n\nCordialement,\nL'équipe CreditSense."
    }
    
    # On sauvegarde aussi les réponses pour les réutiliser plus tard
    joblib.dump(responses, os.path.join(models_dir, "responses.joblib"))
    print("Réponses types sauvegardées dans models/responses.joblib")

if __name__ == "__main__":
    train_and_save_model()

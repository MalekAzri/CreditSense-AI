import pandas as pd
from credit_scoring_qdrant import CreditScoringWithQdrant
import os

def populate():
    # Configuration
    columns = [
        "status_account", "duration", "credit_history", "purpose",
        "credit_amount", "savings", "employment",
        "installment_rate", "personal_status", "other_debtors",
        "residence_since", "property", "age",
        "other_installments", "housing", "existing_credits",
        "job", "people_liable", "telephone", "foreign_worker",
        "risk"
    ]
    
    # Check if data exists
    data_path = "data/raw/german.data"
    if not os.path.exists(data_path):
        print(f"❌ Erreur : Fichier {data_path} introuvable.")
        return

    # Charger les données
    print("📥 Chargement des données historiques...")
    df = pd.read_csv(data_path, sep=" ", names=columns)
    
    # Initialiser le système Qdrant
    print("🚀 Initialisation de Qdrant...")
    system = CreditScoringWithQdrant(qdrant_url="http://localhost:6333")
    
    # On va populer avec l'intégralité des clients pour une base solide
    num_to_index = 1000
    print(f"⚡ Indexation de {num_to_index} clients historiques dans Qdrant...")
    
    for i in range(num_to_index):
        client_data = df.iloc[i].to_dict()
        # Enlever le 'risk' des données client avant le passage dans le système
        # car on veut le calculer ou le comparer
        actual_risk = client_data.pop('risk')
        
        # Le système va calculer le score et l'ajouter à Qdrant
        system.process_new_client(i, client_data)
        
        if (i+1) % 10 == 0:
            print(f"✅ {i+1}/{num_to_index} indexés...")

    print("\n✨ Base de données Qdrant initialisée avec succès !")

if __name__ == "__main__":
    populate()

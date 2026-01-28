"""
Script pour réorganiser les colonnes du fichier german.data 
en regroupant les attributs par type (catégoriel vs numérique)

Attributs du German Credit Dataset:
-----------------------------------
Catégoriels (Qualitative):
- A1: Status of existing checking account
- A3: Credit history
- A4: Purpose
- A6: Savings account/bonds
- A7: Present employment since
- A9: Personal status and sex
- A10: Other debtors/guarantors
- A12: Property
- A14: Other installment plans
- A15: Housing
- A17: Job
- A19: Telephone
- A20: Foreign worker

Numériques (Quantitative):
- A2: Duration in month
- A5: Credit amount
- A8: Installment rate in percentage of disposable income
- A11: Present residence since
- A13: Age in years
- A16: Number of existing credits at this bank
- A18: Number of people being liable to provide maintenance for
- A21: Class (target variable - 1=good, 2=bad)
"""

import pandas as pd

# Définir les noms des colonnes
columns = [
    "status_account",      # A1 - Catégoriel
    "duration",            # A2 - Numérique
    "credit_history",      # A3 - Catégoriel
    "purpose",             # A4 - Catégoriel
    "credit_amount",       # A5 - Numérique
    "savings_account",     # A6 - Catégoriel
    "employment_since",    # A7 - Catégoriel
    "installment_rate",    # A8 - Numérique
    "personal_status_sex", # A9 - Catégoriel
    "other_debtors",       # A10 - Catégoriel
    "residence_since",     # A11 - Numérique
    "property",            # A12 - Catégoriel
    "age",                 # A13 - Numérique
    "other_installment",   # A14 - Catégoriel
    "housing",             # A15 - Catégoriel
    "existing_credits",    # A16 - Numérique
    "job",                 # A17 - Catégoriel
    "num_dependents",      # A18 - Numérique
    "telephone",           # A19 - Catégoriel
    "foreign_worker",      # A20 - Catégoriel
    "class"                # A21 - Numérique (cible)
]

# Colonnes catégorielles (indices 0-based)
categorical_columns = [
    "status_account",      # A1
    "credit_history",      # A3
    "purpose",             # A4
    "savings_account",     # A6
    "employment_since",    # A7
    "personal_status_sex", # A9
    "other_debtors",       # A10
    "property",            # A12
    "other_installment",   # A14
    "housing",             # A15
    "job",                 # A17
    "telephone",           # A19
    "foreign_worker"       # A20
]

# Colonnes numériques
numerical_columns = [
    "duration",            # A2
    "credit_amount",       # A5
    "installment_rate",    # A8
    "residence_since",     # A11
    "age",                 # A13
    "existing_credits",    # A16
    "num_dependents",      # A18
    "class"                # A21 (variable cible)
]

def load_and_reorganize_data():
    """Charger et réorganiser les données german.data"""
    
    # Charger les données
    df = pd.read_csv('german.data', sep=' ', header=None, names=columns)
    
    print("=" * 70)
    print("RÉORGANISATION DES COLONNES DU GERMAN CREDIT DATASET")
    print("=" * 70)
    
    print("\n📊 Données originales:")
    print(f"   - Nombre de lignes: {len(df)}")
    print(f"   - Nombre de colonnes: {len(df.columns)}")
    print(f"\n   Ordre original des colonnes:")
    for i, col in enumerate(columns, 1):
        print(f"   {i:2}. {col}")
    
    # Réorganiser: catégorielles d'abord, puis numériques
    new_column_order = categorical_columns + numerical_columns
    df_reorganized = df[new_column_order]
    
    print("\n" + "=" * 70)
    print("📋 NOUVELLE ORGANISATION DES COLONNES")
    print("=" * 70)
    
    print("\n🔤 ATTRIBUTS CATÉGORIELS (A1, A3, A4, A6, A7, A9, A10, A12, A14, A15, A17, A19, A20):")
    print("-" * 50)
    for i, col in enumerate(categorical_columns, 1):
        unique_values = df[col].nunique()
        print(f"   {i:2}. {col:25} ({unique_values} valeurs uniques)")
    
    print(f"\n🔢 ATTRIBUTS NUMÉRIQUES (A2, A5, A8, A11, A13, A16, A18, A21):")
    print("-" * 50)
    for i, col in enumerate(numerical_columns, 1):
        if col == "class":
            print(f"   {i:2}. {col:25} (Variable cible: 1=bon, 2=mauvais)")
        else:
            min_val = df[col].min()
            max_val = df[col].max()
            mean_val = df[col].mean()
            print(f"   {i:2}. {col:25} (min: {min_val}, max: {max_val}, moyenne: {mean_val:.2f})")
    
    # Sauvegarder le fichier réorganisé
    output_file = 'german_reorganized.data'
    df_reorganized.to_csv(output_file, sep=' ', header=False, index=False)
    print(f"\n✅ Fichier réorganisé sauvegardé: {output_file}")
    
    # Créer aussi une version CSV avec en-têtes
    output_csv = 'german_reorganized.csv'
    df_reorganized.to_csv(output_csv, index=False)
    print(f"✅ Version CSV avec en-têtes: {output_csv}")
    
    print("\n" + "=" * 70)
    print("📄 APERÇU DES PREMIÈRES LIGNES (données réorganisées)")
    print("=" * 70)
    print(df_reorganized.head(10).to_string())
    
    return df_reorganized

if __name__ == "__main__":
    df_reorganized = load_and_reorganize_data()

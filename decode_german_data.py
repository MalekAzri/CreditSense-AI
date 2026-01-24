"""
Script pour décoder et transformer le fichier german.data
en un fichier CSV lisible avec noms de colonnes et valeurs décodées
"""

import pandas as pd

# Noms des colonnes
columns = [
    "compte_courant",           # A1
    "duree_mois",               # A2
    "historique_credit",        # A3
    "objectif_credit",          # A4
    "montant_credit",           # A5
    "epargne",                  # A6
    "emploi_depuis",            # A7
    "taux_remboursement",       # A8
    "statut_personnel",         # A9
    "garants",                  # A10
    "residence_depuis",         # A11
    "patrimoine",               # A12
    "age",                      # A13
    "autres_credits",           # A14
    "logement",                 # A15
    "nb_credits_banque",        # A16
    "emploi",                   # A17
    "personnes_a_charge",       # A18
    "telephone",                # A19
    "travailleur_etranger",     # A20
    "classe"                    # A21 (cible)
]

# Dictionnaires de décodage pour chaque attribut catégoriel

decode_A1_compte = {
    "A11": "< 0 DM (découvert)",
    "A12": "0-200 DM",
    "A13": ">= 200 DM",
    "A14": "Pas de compte"
}

decode_A3_historique = {
    "A30": "Aucun crédit / tous remboursés",
    "A31": "Tous crédits remboursés ici",
    "A32": "Crédits en cours remboursés",
    "A33": "Retards de paiement passés",
    "A34": "Compte critique / autres crédits"
}

decode_A4_objectif = {
    "A40": "Voiture (neuve)",
    "A41": "Voiture (occasion)",
    "A42": "Meubles/Équipement",
    "A43": "Radio/Télévision",
    "A44": "Électroménager",
    "A45": "Réparations",
    "A46": "Éducation",
    "A47": "Vacances",
    "A48": "Reconversion pro",
    "A49": "Business",
    "A410": "Autres"
}

decode_A6_epargne = {
    "A61": "< 100 DM",
    "A62": "100-500 DM",
    "A63": "500-1000 DM",
    "A64": ">= 1000 DM",
    "A65": "Pas d'épargne"
}

decode_A7_emploi = {
    "A71": "Sans emploi",
    "A72": "< 1 an",
    "A73": "1-4 ans",
    "A74": "4-7 ans",
    "A75": ">= 7 ans"
}

decode_A9_statut = {
    "A91": "Homme divorcé/séparé",
    "A92": "Femme divorcée/mariée",
    "A93": "Homme célibataire",
    "A94": "Homme marié/veuf",
    "A95": "Femme célibataire"
}

decode_A10_garants = {
    "A101": "Aucun",
    "A102": "Co-demandeur",
    "A103": "Garant"
}

decode_A12_patrimoine = {
    "A121": "Immobilier",
    "A122": "Épargne logement/Assurance vie",
    "A123": "Voiture ou autre",
    "A124": "Aucun patrimoine"
}

decode_A14_autres_credits = {
    "A141": "Banque",
    "A142": "Magasins",
    "A143": "Aucun"
}

decode_A15_logement = {
    "A151": "Location",
    "A152": "Propriétaire",
    "A153": "Gratuit"
}

decode_A17_emploi_type = {
    "A171": "Sans emploi/Non qualifié (non-résident)",
    "A172": "Non qualifié (résident)",
    "A173": "Qualifié/Employé/Fonctionnaire",
    "A174": "Cadre/Indépendant/Dirigeant"
}

decode_A19_telephone = {
    "A191": "Non",
    "A192": "Oui (à son nom)"
}

decode_A20_etranger = {
    "A201": "Oui",
    "A202": "Non"
}

decode_classe = {
    1: "Bon client",
    2: "Mauvais client"
}


def decode_data():
    """Charger et decoder le fichier german.data"""
    
    # Charger les donnees
    df = pd.read_csv('german.data', sep=' ', header=None, names=columns)
    
    print("=" * 70)
    print("DECODAGE DU GERMAN CREDIT DATASET")
    print("=" * 70)
    print(f"\n[INFO] Chargement de {len(df)} lignes...")
    
    # Creer une copie decodee
    df_decoded = df.copy()
    
    # Decoder chaque colonne categorielle
    print("\n[...] Decodage des colonnes categorielles...")
    
    df_decoded['compte_courant'] = df['compte_courant'].map(decode_A1_compte)
    df_decoded['historique_credit'] = df['historique_credit'].map(decode_A3_historique)
    df_decoded['objectif_credit'] = df['objectif_credit'].map(decode_A4_objectif)
    df_decoded['epargne'] = df['epargne'].map(decode_A6_epargne)
    df_decoded['emploi_depuis'] = df['emploi_depuis'].map(decode_A7_emploi)
    df_decoded['statut_personnel'] = df['statut_personnel'].map(decode_A9_statut)
    df_decoded['garants'] = df['garants'].map(decode_A10_garants)
    df_decoded['patrimoine'] = df['patrimoine'].map(decode_A12_patrimoine)
    df_decoded['autres_credits'] = df['autres_credits'].map(decode_A14_autres_credits)
    df_decoded['logement'] = df['logement'].map(decode_A15_logement)
    df_decoded['emploi'] = df['emploi'].map(decode_A17_emploi_type)
    df_decoded['telephone'] = df['telephone'].map(decode_A19_telephone)
    df_decoded['travailleur_etranger'] = df['travailleur_etranger'].map(decode_A20_etranger)
    df_decoded['classe'] = df['classe'].map(decode_classe)
    
    # Sauvegarder le fichier décodé
    output_file = 'german_decoded.csv'
    df_decoded.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Fichier décodé sauvegardé: {output_file}")
    
    # Afficher les informations sur les colonnes
    print("\n" + "=" * 70)
    print("📋 DESCRIPTION DES COLONNES")
    print("=" * 70)
    
    print("\n🔤 COLONNES CATÉGORIELLES:")
    print("-" * 50)
    categorical_cols = [
        ('compte_courant', 'Statut du compte courant'),
        ('historique_credit', 'Historique de crédit'),
        ('objectif_credit', 'But du crédit'),
        ('epargne', 'Montant de l\'épargne'),
        ('emploi_depuis', 'Ancienneté dans l\'emploi'),
        ('statut_personnel', 'Statut personnel et sexe'),
        ('garants', 'Autres débiteurs/garants'),
        ('patrimoine', 'Type de patrimoine'),
        ('autres_credits', 'Autres plans de crédit'),
        ('logement', 'Type de logement'),
        ('emploi', 'Type d\'emploi'),
        ('telephone', 'Téléphone'),
        ('travailleur_etranger', 'Travailleur étranger')
    ]
    for col, desc in categorical_cols:
        print(f"   • {col:25} : {desc}")
    
    print("\n🔢 COLONNES NUMÉRIQUES:")
    print("-" * 50)
    numerical_cols = [
        ('duree_mois', 'Durée du crédit en mois'),
        ('montant_credit', 'Montant du crédit en DM'),
        ('taux_remboursement', 'Taux de remboursement (% du revenu)'),
        ('residence_depuis', 'Années de résidence actuelle'),
        ('age', 'Âge en années'),
        ('nb_credits_banque', 'Nombre de crédits dans cette banque'),
        ('personnes_a_charge', 'Personnes à charge'),
        ('classe', 'Classification (Bon/Mauvais client)')
    ]
    for col, desc in numerical_cols:
        print(f"   • {col:25} : {desc}")
    
    # Afficher un aperçu
    print("\n" + "=" * 70)
    print("📄 APERÇU DES 5 PREMIÈRES LIGNES")
    print("=" * 70)
    
    # Afficher de façon lisible
    for i in range(5):
        print(f"\n--- Client {i+1} ---")
        for col in df_decoded.columns:
            print(f"   {col:25}: {df_decoded.iloc[i][col]}")
    
    # Statistiques
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES")
    print("=" * 70)
    
    print(f"\n   Distribution de la classe cible:")
    print(f"   {df_decoded['classe'].value_counts().to_string()}")
    
    print(f"\n   Statistiques numériques:")
    print(df[['duree_mois', 'montant_credit', 'age', 'nb_credits_banque']].describe().to_string())
    
    return df_decoded


if __name__ == "__main__":
    df_decoded = decode_data()
    print("\n" + "=" * 70)
    print("✅ TERMINÉ! Ouvrez 'german_decoded.csv' pour voir les données lisibles.")
    print("=" * 70)

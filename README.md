
## 📌 Présentation

Ce projet utilise le Machine Learning pour prédire si un client est capable de rembourser un prêt. Il s'appuie sur le célèbre jeu de données **German Credit** pour entraîner des algorithmes capables de classer les demandes de crédit en deux catégories : **Accordé** ou **Refusé**.

## � Critères de Décision

L'IA analyse plusieurs critères clés pour évaluer le risque :
*   **Situation financière** : État du compte courant, épargne, montant du crédit.
*   **Profil personnel** : Âge, emploi, statut marital, situation de logement.
*   **Historique de crédit** : Comportement de remboursement passé, nombre de crédits existants.
*   **Conditions du prêt** : Durée du crédit, but de l'emprunt (voiture, éducation, etc.).

## �🛠️ Installation

Pour utiliser ce projet, vous devez avoir Python installé. Installez ensuite les dépendances nécessaires avec la commande suivante :

```bash
pip install pandas numpy scikit-learn
```

## 🚀 Comment l'utiliser ?

Le projet est organisé de manière logique pour faciliter son utilisation :

1. **Préparer les données** :
   Le script `src/load_data.py` permet de charger les informations de base.
   
2. **Entraîner l'IA** :
   Lancez le script principal pour créer le modèle prédictif :
   ```bash
   python src/credit_scoring.py
   ```
   Ce script compare plusieurs modèles et sauvegarde le plus performant dans le dossier `models/`.

3. **Tester un client** :
   Pour voir l'IA en action sur un cas concret, utilisez :
   ```bash
   python src/test_new_client.py
   ```

## 📂 Structure du Dossier

*   **`src/`** : Le cœur du projet (scripts de traitement et d'entraînement).
*   **`data/`** : Contient les fichiers de données (données brutes et transformées).
*   **`models/`** : Emplacement du modèle final sauvegardé.
*   **`README.md`** : Ce guide que vous lisez actuellement.

## 🧠 Technologies utilisées

*   **Python** : Langage de programmation principal.
*   **Pandas & Numpy** : Pour la manipulation des données.
*   **Scikit-Learn** : Pour la partie Intelligence Artificielle (Random Forest, Régression Logistique).

---
*Projet réalisé dans le cadre de l'apprentissage du Machine Learning appliqué à la finance.*

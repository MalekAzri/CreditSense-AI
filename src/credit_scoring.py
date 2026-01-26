import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_score, recall_score
import pickle

# ==========================================
# 1. PRÉPARATION DES DONNÉES (SILENCIEUX)
# ==========================================
columns = [
    "status_account", "duration", "credit_history", "purpose",
    "credit_amount", "savings", "employment",
    "installment_rate", "personal_status", "other_debtors",
    "residence_since", "property", "age",
    "other_installments", "housing", "existing_credits",
    "job", "people_liable", "telephone", "foreign_worker",
    "risk"
]

df = pd.read_csv("data/raw/german.data", sep=" ", names=columns)
df['risk'] = df['risk'].map({1: 0, 2: 1})

X = df.drop('risk', axis=1)
y = df['risk']

categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
final_columns = X_encoded.columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ==========================================
# 2. ENTRAÎNEMENT ET OPTIMISATION
# ==========================================
# Régression Logistique
log_reg = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
log_reg.fit(X_train_scaled, y_train)

# Random Forest (GridSearch rapide)
rf_params = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10],
    'class_weight': ['balanced', None]
}
grid_search_rf = GridSearchCV(RandomForestClassifier(random_state=42), rf_params, cv=5, scoring='roc_auc', n_jobs=-1)
grid_search_rf.fit(X_train_scaled, y_train)
best_rf = grid_search_rf.best_estimator_

# Gradient Boosting (Souvent plus précis que RF)
gb_params = {
    'n_estimators': [100, 200],
    'learning_rate': [0.05, 0.1],
    'max_depth': [3, 5]
}
grid_search_gb = GridSearchCV(GradientBoostingClassifier(random_state=42), gb_params, cv=5, scoring='roc_auc', n_jobs=-1)
grid_search_gb.fit(X_train_scaled, y_train)
best_gb = grid_search_gb.best_estimator_

# ==========================================
# 3. COLLECTE DES RÉSULTATS POUR AFFICHAGE UNIQUE
# ==========================================
results = []
models = [
    ("LR (Baseline)", log_reg), 
    ("RF (Random Forest)", best_rf),
    ("GB (Gradient Boosting)", best_gb)
]

for name, model in models:
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    # K-Fold Cross Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='roc_auc')
    
    results.append({
        "Modèle": name,
        "CV AUC Moyenne": f"{cv_scores.mean():.3f} (+/- {cv_scores.std()*2:.3f})",
        "Test AUC": f"{roc_auc_score(y_test, y_proba):.3f}",
        "Précision": f"{precision_score(y_test, y_pred):.3f}",
        "Rappel": f"{recall_score(y_test, y_pred):.3f}"
    })

# Sauvegarde
with open('models/credit_scoring_model.pkl', 'wb') as f:
    pickle.dump({'model': best_rf, 'scaler': scaler, 'columns': final_columns}, f)

# ==========================================
# 4. AFFICHAGE UNIQUE FINAL
# ==========================================
print("\n" + "="*50)
print("  RAPPORT DE PERFORMANCE DU MODÈLE DE CRÉDIT")
print("="*50)
print(pd.DataFrame(results).to_string(index=False))
print("-" * 50)
print("Statut : Modèle optimisé et sauvegardé avec succès.")
print("="*50 + "\n")

def calculer_score_credit(client_data, model, scaler, final_columns):
    client_df = pd.DataFrame([client_data])
    client_encoded = pd.get_dummies(client_df)
    for col in final_columns:
        if col not in client_encoded.columns:
            client_encoded[col] = 0
    client_encoded = client_encoded[final_columns]
    client_scaled = scaler.transform(client_encoded)
    proba_risque = model.predict_proba(client_scaled)[0, 1]
    score = (1 - proba_risque) * 100
    decision = "ACCEPTÉ" if score >= 50 else "REFUSÉ"
    return score, decision, proba_risque

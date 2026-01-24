import pandas as pd

columns = [
    "status_account", "duration", "credit_history", "purpose",
    "credit_amount", "savings", "employment",
    "installment_rate", "personal_status", "other_debtors",
    "residence_since", "property", "age",
    "other_installments", "housing", "existing_credits",
    "job", "people_liable", "telephone", "foreign_worker",
    "risk"
]

df = pd.read_csv("german.data", sep=" ", names=columns)
print(df.head())

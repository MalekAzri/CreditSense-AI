import pandas as pd
import random

def generate_dataset():
    data = []
    
    # 1. Documents required
    docs_questions = [
        "Quels sont les documents nécessaires pour un crédit ?",
        "Liste des pièces à fournir pour un prêt bancaire ?",
        "Qu'est-ce qu'il faut comme papiers pour demander un crédit ?",
        "Quels justificatifs dois-je préparer pour mon dossier de crédit ?",
        "Pouvez-vous m'envoyer la liste des documents pour un prêt ?",
        "Documents recommandés pour un crédit immobilier ?",
        "Que faut-il fournir pour une demande de financement ?",
        "Pièces justificatives pour un crédit à la consommation ?",
        "Quels sont les docs nécessaires ?",
        "J'aimerais savoir quels documents préparer pour ma demande.",
        "Liste documents crédit bancaire",
        "Quels papiers pour un prêt ?",
        "Quels sont les éléments à fournir pour l'étude de mon dossier ?",
        "Pouvez-vous m'indiquer les documents à joindre ?",
        "Quels documents pour un rachat de crédit ?",
        "Quels papiers dois-je envoyer ?",
        "C'est quoi la liste des docs ?",
        "J'ai besoin de la liste des pièces justificatives.",
        "Quels sont les justificatifs de revenus ?",
        "Faut-il un avis d'imposition ?",
        "Quels documents pour prouver mon identité ?",
        "Papiers nécessaires dossier bancaire.",
        "Que manque-t-il dans mon dossier ?",
        "Quelles sont les pièces manquantes ?",
        "Dites-moi ce qu'il faut envoyer.",
        "Mon dossier est-il complet ?",
        "Est-ce qu'il manque des documents ?",
        "Quels sont les éléments manquants pour mon prêt ?",
        "Je voudrais savoir si j'ai tout envoyé.",
        "Liste documents manquants svp.",
        "Vérifiez si mon dossier est complet.",
        "Il manque quoi pour valider mon crédit ?"
    ]
    
    # 2. Status request
    status_questions = [
        "Quel est le statut de ma demande de crédit ?",
        "Où en est mon dossier de prêt ?",
        "Je n'ai pas de nouvelles de ma demande de crédit.",
        "Pouvez-vous me dire si mon crédit est accepté ?",
        "Statut de ma demande de prêt s'il vous plaît.",
        "Est-ce que mon dossier a été validé ?",
        "Suivi de dossier de crédit",
        "Je voudrais savoir si ma demande avance.",
        "Quand aurai-je une réponse pour mon prêt ?",
        "Ma demande de crédit est-elle en cours de traitement ?",
        "Avancement de ma demande de financement",
        "Le statut de ma demande ?",
        "Suivre mon dossier de prêt",
        "Ma demande a-t-elle été examinée ?",
        "Réponse pour mon crédit ?",
        "Des nouvelles de mon dossier ?",
        "Est-ce que mon prêt est en cours ?",
        "J'attends une réponse depuis longtemps.",
        "Où en sommes-nous pour ma demande ?",
        "Statut dossier CS-001",
        "Suivi de prêt immo.",
        "Est-ce que c'est accepté ?",
        "Délai pour une réponse ?",
        "Pourquoi mon dossier n'avance pas ?",
        "Ma demande est-elle validée ?",
        "Avancement du dossier de financement.",
        "Je n'ai pas eu de retour sur ma demande.",
        "Bonjour, des nouvelles de mon crédit ?"
    ]
    
    # 3. Others (Noise)
    other_questions = [
        "Bonjour, comment allez-vous ?",
        "Je voudrais prendre rendez-vous avec un conseiller.",
        "Quels sont vos horaires d'ouverture ?",
        "Merci pour votre aide.",
        "C'est urgent, rappelez-moi.",
        "Je souhaite clôturer mon compte.",
        "Comment changer mon mot de passe ?",
        "Où se trouve votre agence ?",
        "Je veux parler à un responsable.",
        "Pouvez-vous m'aider avec mon application mobile ?",
        "Aurevoir.",
        "Merci beaucoup.",
        "Puis-je avoir un rendez-vous ?",
        "Je voudrais parler à quelqu'un.",
        "Quelle heure est-il ?",
        "J'ai un problème avec ma carte bleue.",
        "Comment activer mon compte ?"
    ]

    # Augmentation simple (mélange de mots et variations)
    def augment(texts, label, count=100):
        augmented = []
        for _ in range(count):
            base = random.choice(texts)
            # On peut ajouter des variations légères (majuscules, ponctuation)
            if random.random() > 0.5:
                base = base.lower()
            if random.random() > 0.8:
                base = base.replace("?", "")
            augmented.append({"text": base, "label": label})
        return augmented

    data.extend(augment(docs_questions, "document_request", 300))
    data.extend(augment(status_questions, "status_request", 300))
    data.extend(augment(other_questions, "other", 100))
    
    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True) # Shuffle
    df.to_csv("data/credit_emails.csv", index=False, encoding='utf-8')
    print(f"Dataset généré avec {len(df)} lignes dans data/credit_emails.csv")

if __name__ == "__main__":
    generate_dataset()

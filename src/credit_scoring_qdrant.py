import pandas as pd
import numpy as np
import pickle
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import json

class CreditScoringWithQdrant:
    def __init__(self, qdrant_url="http://localhost:6333"):
        """
        Initialise le système de scoring avec Qdrant
        """
        # Connexion à Qdrant
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = "credit_clients"
        
        # Modèle d'embedding pour convertir les profils en vecteurs
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Charger le modèle ML
        self.load_ml_model()
        
        # Créer la collection Qdrant si elle n'existe pas
        self.setup_collection()
    
    def load_ml_model(self):
        """Charge le modèle ML sauvegardé"""
        try:
            with open('models/credit_scoring_model.pkl', 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.final_columns = data['columns']
            print("✅ Modèle ML chargé avec succès")
        except FileNotFoundError:
            print("❌ Erreur : Modèle ML introuvable. Lancez d'abord credit_scoring.py")
            raise
    
    def setup_collection(self):
        """Crée la collection Qdrant pour stocker les profils clients"""
        try:
            # Vérifier si la collection existe
            collections = self.client.get_collections().collections
            exists = any(col.name == self.collection_name for col in collections)
            
            if not exists:
                # Créer la collection avec dimension 384 (pour all-MiniLM-L6-v2)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"✅ Collection '{self.collection_name}' créée")
            else:
                print(f"✅ Collection '{self.collection_name}' existe déjà")
        except Exception as e:
            print(f"❌ Erreur lors de la création de la collection: {e}")
            raise
    
    def client_to_text(self, client_data):
        """
        Convertit les données d'un client en texte pour l'embedding
        """
        text_parts = []
        # On définit un ordre fixe pour la consistance des embeddings
        ordered_keys = sorted(client_data.keys())
        for key in ordered_keys:
            value = client_data[key]
            text_parts.append(f"{key}: {value}")
        return " | ".join(text_parts)
    
    def calculer_score_credit(self, client_data):
        """
        Calcule le score de crédit d'un client
        """
        # Création du DataFrame
        client_df = pd.DataFrame([client_data])
        
        # Encodage One-Hot
        client_encoded = pd.get_dummies(client_df)
        
        if self.model is None or self.scaler is None:
            raise RuntimeError("❌ Erreur : Modèle ou Scaler non chargé. Vérifiez le dossier 'models/'.")

        # Réalignement des colonnes
        for col in self.final_columns:
            if col not in client_encoded.columns:
                client_encoded[col] = 0
                
        # Filtrer uniquement les colonnes attendues dans le bon ordre
        client_encoded = client_encoded[self.final_columns]
        
        # Normalisation
        client_scaled = self.scaler.transform(client_encoded)
        
        # Prédiction
        proba_risque = self.model.predict_proba(client_scaled)[0, 1]
        score = (1 - proba_risque) * 100
        decision = "ACCEPTÉ" if score >= 50 else "REFUSÉ"
        
        return score, decision, proba_risque
    
    def add_client_to_qdrant(self, client_id, client_data, score, decision, proba_risque):
        """
        Ajoute un profil client dans Qdrant
        """
        # Convertir les données en texte
        client_text = self.client_to_text(client_data)
        
        # Générer l'embedding vectoriel
        vector = self.encoder.encode(client_text).tolist()
        
        # Préparer le payload (métadonnées)
        payload = {
            "client_id": client_id,
            "score": float(score),
            "decision": decision,
            "proba_risque": float(proba_risque),
            "data": client_data
        }
        
        # Insérer dans Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=client_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        print(f"✅ Client {client_id} ajouté à Qdrant")
    
    def find_similar_clients(self, client_data, top_k=5):
        """
        Trouve les clients similaires dans Qdrant
        """
        # Convertir en texte et générer l'embedding
        client_text = self.client_to_text(client_data)
        query_vector = self.encoder.encode(client_text).tolist()
        
        # Recherche dans Qdrant
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        ).points
        
        return results
    
    def process_new_client(self, client_id, client_data):
        """
        Pipeline complet : scoring + recherche de similarité + stockage
        """
        print("\n" + "="*60)
        print(f"  ANALYSE DU CLIENT #{client_id}")
        print("="*60)
        
        # 1. Calculer le score
        score, decision, proba = self.calculer_score_credit(client_data)
        
        print(f"\n📊 RÉSULTATS DU SCORING:")
        print(f"   Score de fiabilité    : {score:.1f}/100")
        print(f"   Probabilité de risque : {proba:.2%}")
        print(f"   Décision finale       : {decision}")
        
        # 2. Rechercher des clients similaires
        print(f"\n🔍 RECHERCHE DE CLIENTS SIMILAIRES:")
        similar_clients = self.find_similar_clients(client_data, top_k=3)
        
        if similar_clients:
            print(f"   Trouvé {len(similar_clients)} client(s) similaire(s):")
            for i, result in enumerate(similar_clients, 1):
                print(f"\n   {i}. Client #{result.id}")
                print(f"      - Similarité      : {result.score:.2%}")
                print(f"      - Score           : {result.payload['score']:.1f}/100")
                print(f"      - Décision        : {result.payload['decision']}")
        else:
            print("   Aucun client similaire trouvé dans la base")
        
        # 3. Ajouter à Qdrant
        self.add_client_to_qdrant(client_id, client_data, score, decision, proba)
        
        print("\n" + "="*60 + "\n")
        
        return {
            "score": score,
            "decision": decision,
            "proba_risque": proba,
            "similar_clients": similar_clients
        }


# ==========================================
# EXEMPLE D'UTILISATION
# ==========================================
def main():
    # Initialiser le système
    print("🚀 Initialisation du système de scoring avec Qdrant...")
    system = CreditScoringWithQdrant(qdrant_url="http://localhost:6333")
    
    # Exemples de clients
    clients = [
        {
            "id": 1001,
            "data": {
                'status_account': 'A11',
                'duration': 6,
                'credit_history': 'A34',
                'purpose': 'A43',
                'credit_amount': 1169,
                'savings': 'A65',
                'employment': 'A75',
                'installment_rate': 4,
                'personal_status': 'A93',
                'other_debtors': 'A101',
                'residence_since': 4,
                'property': 'A121',
                'age': 67,
                'other_installments': 'A143',
                'housing': 'A152',
                'existing_credits': 2,
                'job': 'A173',
                'people_liable': 1,
                'telephone': 'A192',
                'foreign_worker': 'A201'
            }
        },
        {
            "id": 1002,
            "data": {
                'status_account': 'A13',
                'duration': 24,
                'credit_history': 'A33',
                'purpose': 'A41',
                'credit_amount': 1500,
                'savings': 'A61',
                'employment': 'A73',
                'installment_rate': 3,
                'personal_status': 'A93',
                'other_debtors': 'A101',
                'residence_since': 4,
                'property': 'A121',
                'age': 53,
                'other_installments': 'A143',
                'housing': 'A151',
                'existing_credits': 0,
                'job': 'A174',
                'people_liable': 1,
                'telephone': 'A191',
                'foreign_worker': 'A201'
            }
        }
    ]
    
    # Traiter chaque client
    for client in clients:
        system.process_new_client(client["id"], client["data"])
    
    print("\n✅ Tous les clients ont été traités avec succès!")


if __name__ == "__main__":
    main()
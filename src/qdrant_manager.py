from qdrant_client import QdrantClient

class QdrantManager:
    def __init__(self, url="http://localhost:6333"):
        self.client = QdrantClient(url=url)
        self.collection_name = "credit_clients"
    
    def get_stats(self):
        """Affiche les statistiques de la collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            print("\n" + "="*50)
            print("  STATISTIQUES QDRANT")
            print("="*50)
            print(f"Collection    : {info.config.params.vectors.size} dimensions")
            print(f"Total points  : {info.points_count}")
            print(f"Distance      : {info.config.params.vectors.distance}")
            print("="*50 + "\n")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def list_all_clients(self):
        """Liste tous les clients stockés"""
        try:
            points = self.client.scroll(
                collection_name=self.collection_name,
                limit=100
            )[0]
            
            print("\n" + "="*50)
            print(f"  LISTE DES CLIENTS ({len(points)} trouvés)")
            print("="*50)
            
            for point in points:
                print(f"\nClient #{point.id}")
                print(f"  Score    : {point.payload['score']:.1f}/100")
                print(f"  Décision : {point.payload['decision']}")
                print(f"  Risque   : {point.payload['proba_risque']:.2%}")
            
            print("="*50 + "\n")
        except Exception as e:
            print(f"❌ Erreur : {e}")
    
    def delete_collection(self):
        """Supprime la collection (attention !)"""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"✅ Collection '{self.collection_name}' supprimée")
        except Exception as e:
            print(f"❌ Erreur : {e}")


if __name__ == "__main__":
    manager = QdrantManager()
    manager.get_stats()
    manager.list_all_clients()

"""
Service Qdrant pour la gestion des vecteurs d'embeddings
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
from app.core.config import (
    QDRANT_URL, 
    QDRANT_COLLECTION_NAME, 
    QDRANT_VECTOR_SIZE, 
    QDRANT_API_KEY
)


class QdrantService:
    """
    Service pour interagir avec Qdrant Cloud
    """
    
    def __init__(self):
        """
        Initialise la connexion à Qdrant Cloud
        """
        print(f"🔗 Connexion à Qdrant Cloud...")
        self.client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=30  # Timeout de 30 secondes
        )
        self.collection_name = QDRANT_COLLECTION_NAME
        print(f"✅ Client Qdrant initialisé")
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """
        Crée la collection si elle n'existe pas
        """
        try:
            print(f"🔍 Vérification de la collection '{self.collection_name}'...")
            
            # Vérifier si la collection existe
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                print(f"📦 Création de la collection Qdrant : {self.collection_name}")
                
                # Créer la collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=QDRANT_VECTOR_SIZE,
                        distance=Distance.COSINE  # Similarité cosinus
                    )
                )
                print(f"✅ Collection {self.collection_name} créée avec succès")
            else:
                print(f"✅ Collection {self.collection_name} déjà existante")
        
        except Exception as e:
            print(f"❌ Erreur lors de la création/vérification de la collection : {e}")
            raise
    
    def insert_audio_vector(
        self,
        audio_id: int,
        vector: List[float],
        metadata: Dict
    ) -> int:
        """
        Insère un vecteur audio dans Qdrant
        
        Args:
            audio_id: ID de l'audio dans la DB
            vector: Vecteur d'embedding (384 dimensions)
            metadata: Métadonnées (sentiment, stress, langue, etc.)
        
        Returns:
            point_id: ID du point dans Qdrant (integer)
        """
        point_id = audio_id  # ✅ Utiliser directement l'integer
        
        try:
            # Ajouter audio_id dans les métadonnées pour retrouver facilement
            metadata_with_id = {
                "audio_id": audio_id,
                **metadata
            }
            
            # Créer le point
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=metadata_with_id
            )
            
            # Insérer dans Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"✅ Vecteur audio_{audio_id} inséré dans Qdrant")
            return point_id
        
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion dans Qdrant : {e}")
            raise
    
    def search_similar_audios(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Recherche les audios les plus similaires
        
        Args:
            query_vector: Vecteur de l'audio à comparer
            limit: Nombre de résultats à retourner
            score_threshold: Score minimum de similarité (0-1)
            filters: Filtres optionnels (ex: {"language": "fr"})
        
        Returns:
            Liste de résultats avec id, score et metadata
        """
        try:
            # Construire les filtres Qdrant
            qdrant_filter = None
            if filters:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                
                qdrant_filter = Filter(must=conditions)
            
            # Recherche (utilisation de query_points pour qdrant-client >= 1.7)
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=qdrant_filter
            ).points
            
            # Formater les résultats
            similar_audios = []
            for result in results:
                similar_audios.append({
                    "point_id": result.id,
                    "audio_id": result.payload.get("audio_id", result.id),  # ✅ Depuis metadata
                    "similarity_score": result.score,
                    "metadata": result.payload
                })
            
            print(f"🔍 {len(similar_audios)} audios similaires trouvés")
            return similar_audios
        
        except Exception as e:
            print(f"❌ Erreur lors de la recherche Qdrant : {e}")
            raise
    
    def get_audio_vector(self, audio_id: int) -> Optional[Dict]:
        """
        Récupère un vecteur par audio_id
        
        Args:
            audio_id: ID de l'audio
        
        Returns:
            Dict avec le vecteur et les métadonnées ou None
        """
        point_id = audio_id  # ✅ Integer
        
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id]
            )
            
            if result:
                return {
                    "point_id": result[0].id,
                    "vector": result[0].vector,
                    "metadata": result[0].payload
                }
            return None
        
        except Exception as e:
            print(f"❌ Erreur lors de la récupération : {e}")
            return None
    
    def delete_audio_vector(self, audio_id: int) -> bool:
        """
        Supprime un vecteur de Qdrant
        
        Args:
            audio_id: ID de l'audio
        
        Returns:
            True si supprimé, False sinon
        """
        point_id = audio_id  # ✅ Integer
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            print(f"🗑️ Vecteur audio_{audio_id} supprimé de Qdrant")
            return True
        
        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")
            return False
    
    def get_collection_info(self) -> Dict:
        """
        Récupère les infos de la collection
        
        Returns:
            Dict avec nombre de vecteurs, config, etc.
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des infos : {e}")
            return {}


# Instance globale (singleton)
_qdrant_service = None

def get_qdrant_service() -> QdrantService:
    """
    Retourne l'instance singleton de QdrantService
    """
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service
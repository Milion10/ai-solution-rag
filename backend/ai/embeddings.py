"""
Module de génération d'embeddings vectoriels
Utilise sentence-transformers pour convertir du texte en vecteurs
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """
    Génère des embeddings vectoriels à partir de texte
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialise le générateur d'embeddings
        
        Args:
            model_name: Nom du modèle sentence-transformers
                - all-MiniLM-L6-v2: 384 dims, léger, rapide (recommandé)
                - paraphrase-multilingual-MiniLM-L12-v2: 384 dims, multilingue
                - all-mpnet-base-v2: 768 dims, plus précis mais plus lourd
        """
        self.model_name = model_name
        
        logger.info(f"Chargement du modèle d'embeddings: {model_name}")
        
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"✅ Modèle chargé: {model_name} ({self.embedding_dim} dimensions)")
        
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            raise
    
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Génère un embedding pour un texte
        
        Args:
            text: Texte à transformer en vecteur
        
        Returns:
            Vecteur numpy de dimension self.embedding_dim
        """
        if not text or not text.strip():
            logger.warning("Texte vide fourni pour embedding")
            return np.zeros(self.embedding_dim)
        
        # Générer embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        return embedding
    
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Génère des embeddings pour une liste de textes (plus rapide en batch)
        
        Args:
            texts: Liste de textes
            batch_size: Taille des batchs pour l'encodage
        
        Returns:
            Array numpy de shape (len(texts), embedding_dim)
        """
        if not texts:
            logger.warning("Liste de textes vide")
            return np.array([])
        
        logger.info(f"Génération embeddings pour {len(texts)} textes...")
        
        # Générer embeddings en batch
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,  # Afficher barre de progression si > 100 textes
            convert_to_numpy=True
        )
        
        logger.info(f"✅ {len(embeddings)} embeddings générés")
        
        return embeddings
    
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcule la similarité cosine entre deux embeddings
        
        Args:
            embedding1: Premier vecteur
            embedding2: Deuxième vecteur
        
        Returns:
            Score de similarité entre 0 et 1
        """
        from numpy.linalg import norm
        
        # Similarité cosine
        similarity = np.dot(embedding1, embedding2) / (norm(embedding1) * norm(embedding2))
        
        return float(similarity)


# Instance globale (singleton)
_embeddings_instance = None

def get_embeddings_generator() -> EmbeddingsGenerator:
    """Retourne l'instance singleton du générateur d'embeddings"""
    global _embeddings_instance
    if _embeddings_instance is None:
        # Utiliser config centralisée
        try:
            from config import settings
            model_name = settings.embeddings_model
        except ImportError:
            # Fallback pour tests isolés
            model_name = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
        
        _embeddings_instance = EmbeddingsGenerator(model_name)
    return _embeddings_instance


if __name__ == "__main__":
    # Test du générateur d'embeddings
    generator = EmbeddingsGenerator()
    
    print(f"\n🤖 Modèle: {generator.model_name}")
    print(f"📐 Dimensions: {generator.embedding_dim}\n")
    
    # Test avec quelques phrases
    texts = [
        "L'intelligence artificielle transforme le monde",
        "AI is transforming the world",
        "Le chat dort sur le canapé"
    ]
    
    embeddings = generator.generate_embeddings(texts)
    
    print(f"✅ Généré {len(embeddings)} embeddings\n")
    
    # Calcul similarités
    print("Similarités:")
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            sim = generator.compute_similarity(embeddings[i], embeddings[j])
            print(f"  '{texts[i][:30]}...' vs '{texts[j][:30]}...': {sim:.3f}")

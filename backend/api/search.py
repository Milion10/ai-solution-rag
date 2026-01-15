"""
API Routes pour recherche et chat
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
from ai.vector_store import get_vector_store

logger = logging.getLogger(__name__)
router = APIRouter()


class SearchRequest(BaseModel):
    """Requête de recherche"""
    query: str
    top_k: int = 5
    similarity_threshold: float = 0.5


class SearchResult(BaseModel):
    """Résultat de recherche"""
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    filename: str
    file_type: str
    scope: str
    similarity: float


@router.post("/search", response_model=List[SearchResult])
async def search_documents(request: SearchRequest):
    """
    Recherche par similarité vectorielle dans les documents indexés
    
    Args:
        query: Texte de la requête
        top_k: Nombre de résultats max
        similarity_threshold: Seuil de similarité (0-1)
    
    Returns:
        Liste des chunks les plus similaires avec scores
    """
    try:
        vector_store = get_vector_store()
        
        results = vector_store.search_similar(
            query_text=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        return results
    
    except Exception as e:
        logger.error(f"Erreur recherche: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/test")
async def test_search(q: str = "intelligence artificielle"):
    """
    Endpoint de test rapide pour la recherche
    """
    try:
        vector_store = get_vector_store()
        
        results = vector_store.search_similar(
            query_text=q,
            top_k=3,
            similarity_threshold=0.3
        )
        
        return {
            "query": q,
            "results_count": len(results),
            "results": results
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "message": "Assurez-vous qu'au moins un document est indexé"
        }

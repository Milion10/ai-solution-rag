"""
API Routes pour le chat RAG
Endpoint principal pour conversations avec LLM + recherche vectorielle
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import logging
from ai.vector_store import get_vector_store
from ai.llm import get_llm_generator

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    """Requête de chat"""
    query: str = Field(None, description="Question de l'utilisateur (deprecated, use 'question')", min_length=1)
    question: str = Field(None, description="Question de l'utilisateur", min_length=1)
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur pour filtrer les documents")
    organization_id: Optional[str] = Field(None, description="ID de l'organisation pour filtrer les documents")
    top_k: int = Field(default=5, description="Nombre de chunks à récupérer", ge=1, le=20)
    similarity_threshold: float = Field(default=0.3, description="Seuil de similarité (0-1)", ge=0.0, le=1.0)
    temperature: Optional[float] = Field(default=None, description="Température LLM (0-1)", ge=0.0, le=1.0)
    
    @property
    def user_query(self) -> str:
        """Retourne la question (supporte query et question pour compatibilité)"""
        return self.question or self.query


class Source(BaseModel):
    """Source citée dans la réponse"""
    filename: str
    chunk_index: int
    similarity: float


class ChatResponse(BaseModel):
    """Réponse du chat"""
    query: str
    answer: str
    sources: List[Source]
    confidence: float
    context_used: int
    chunks_found: int


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal du chat RAG
    
    Process:
    1. Recherche chunks similaires dans pgvector
    2. Construit contexte à partir des chunks
    3. Génère réponse avec LLM + contexte
    4. Retourne réponse + sources citées
    
    Args:
        request: ChatRequest avec query, top_k, similarity_threshold
    
    Returns:
        ChatResponse avec answer, sources, confidence
    """
    logger.info(f"💬 Chat request: '{request.user_query[:50]}...'")
    
    try:
        # 1. Recherche vectorielle (avec filtrage par user_id et organization_id si fourni)
        vector_store = get_vector_store()
        chunks = vector_store.search_similar(
            query_text=request.user_query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            user_id=request.user_id,
            organization_id=request.organization_id
        )
        
        if not chunks:
            logger.warning("Aucun chunk trouvé pour la requête")
            return ChatResponse(
                query=request.user_query,
                answer="Je n'ai pas trouvé d'informations pertinentes dans les documents pour répondre à votre question. Pourriez-vous reformuler ou être plus précis ?",
                sources=[],
                confidence=0.0,
                context_used=0,
                chunks_found=0
            )
        
        logger.info(f"  📚 {len(chunks)} chunks récupérés")
        
        # 2. Génération RAG
        llm = get_llm_generator()
        
        # Vérifier si Ollama est disponible
        if not llm.check_health():
            raise HTTPException(
                status_code=503,
                detail="Le service LLM (Ollama) n'est pas disponible. Veuillez vérifier qu'Ollama est installé et démarré."
            )
        
        rag_result = llm.generate_rag_response(
            query=request.user_query,
            context_chunks=chunks,
            max_context_length=3000
        )
        
        logger.info(f"  ✅ Réponse générée (confidence: {rag_result['confidence']}%)")
        
        # 3. Formater la réponse
        return ChatResponse(
            query=request.user_query,
            answer=rag_result["answer"],
            sources=[Source(**s) for s in rag_result["sources"]],
            confidence=rag_result["confidence"],
            context_used=rag_result["context_used"],
            chunks_found=len(chunks)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur chat: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de la requête: {str(e)}")


@router.get("/chat/health")
async def chat_health():
    """
    Vérifie la santé du service de chat
    
    Returns:
        Status du LLM (Ollama) et du vector store
    """
    try:
        llm = get_llm_generator()
        ollama_available = llm.check_health()
        
        vector_store = get_vector_store()
        
        return {
            "status": "healthy" if ollama_available else "degraded",
            "ollama_available": ollama_available,
            "ollama_model": llm.model,
            "vector_store_initialized": True,
            "embedding_dim": vector_store.embedding_dim,
            "message": "Service chat opérationnel" if ollama_available else "Ollama non disponible - installez et démarrez Ollama"
        }
    
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return {
            "status": "unhealthy",
            "ollama_available": False,
            "error": str(e)
        }


@router.get("/chat/test")
async def chat_test(q: str = "Quelle est la vision du produit ?"):
    """
    Endpoint de test rapide du chat
    
    Args:
        q: Question de test (query parameter)
    
    Returns:
        Réponse du chat avec sources
    """
    request = ChatRequest(query=q, top_k=3, similarity_threshold=0.3)
    return await chat(request)

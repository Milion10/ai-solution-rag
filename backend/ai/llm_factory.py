"""
Factory pour créer le bon provider LLM selon la configuration
Supporte Ollama (local) et Groq (cloud)
"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class BaseLLMProvider:
    """Classe de base pour tous les providers LLM"""
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Génère une réponse à partir d'un prompt"""
        raise NotImplementedError
    
    def check_health(self) -> bool:
        """Vérifie si le service est disponible"""
        raise NotImplementedError
    
    def generate_rag_response(
        self,
        query: str,
        context_chunks: list,
        max_context_length: int = 3000
    ) -> Dict:
        """Génère une réponse RAG"""
        raise NotImplementedError
    
    def generate_general_response(self, query: str) -> Dict:
        """Génère une réponse générale sans contexte"""
        raise NotImplementedError


class GroqProvider(BaseLLMProvider):
    """Provider pour Groq API (cloud, rapide)"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "mixtral-8x7b-32768",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        """
        Initialise le provider Groq
        
        Args:
            api_key: Clé API Groq
            model: Modèle à utiliser (mixtral-8x7b-32768, llama-3.1-70b-versatile)
            temperature: Contrôle la créativité (0.0-1.0)
            max_tokens: Nombre maximum de tokens générés
        """
        try:
            from groq import Groq
        except ImportError:
            raise ImportError(
                "Le package 'groq' n'est pas installé. "
                "Installez-le avec: pip install groq"
            )
        
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        logger.info(f"✅ GroqProvider initialisé: {model}")
    
    def check_health(self) -> bool:
        """Vérifie si Groq API est disponible"""
        try:
            # Test simple avec un prompt court
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"❌ Groq non disponible: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Génère une réponse avec Groq
        
        Args:
            prompt: Question ou instruction utilisateur
            system_prompt: Instructions système optionnelles
            temperature: Override température par défaut
            max_tokens: Override max_tokens par défaut
        
        Returns:
            Texte généré
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            generated_text = response.choices[0].message.content
            logger.info(f"✅ Réponse Groq générée: {len(generated_text)} caractères")
            
            return generated_text
        
        except Exception as e:
            logger.error(f"❌ Erreur génération Groq: {e}")
            raise
    
    def generate_rag_response(
        self,
        query: str,
        context_chunks: list,
        max_context_length: int = 3000
    ) -> Dict:
        """
        Génère une réponse RAG avec Groq
        """
        # 1. Construire le contexte
        context_parts = []
        sources = []
        total_length = 0
        
        for chunk in context_chunks:
            chunk_text = f"[Document: {chunk['filename']}, Score: {chunk['similarity']:.2f}]\n{chunk['content']}\n"
            
            if total_length + len(chunk_text) > max_context_length:
                break
            
            context_parts.append(chunk_text)
            sources.append({
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "similarity": chunk["similarity"]
            })
            total_length += len(chunk_text)
        
        context = "\n---\n".join(context_parts)
        
        # 2. Prompt RAG
        system_prompt = """Tu es un assistant IA expert qui répond aux questions en te basant UNIQUEMENT sur le contexte fourni.

Règles importantes:
- Réponds UNIQUEMENT avec les informations présentes dans le contexte
- Si l'information n'est pas dans le contexte, dis "Je n'ai pas cette information dans les documents fournis"
- Cite toujours tes sources en mentionnant le document utilisé
- Sois précis, concis et structuré dans tes réponses
- Utilise un ton professionnel mais accessible"""

        user_prompt = f"""Contexte (documents de l'entreprise):
{context}

Question de l'utilisateur:
{query}

Réponds à la question en te basant sur le contexte ci-dessus. Structure ta réponse clairement et cite tes sources."""

        # 3. Générer la réponse
        try:
            answer = self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # 4. Calculer confiance
            if context_chunks:
                avg_similarity = sum(c["similarity"] for c in context_chunks[:3]) / min(3, len(context_chunks))
                confidence = min(avg_similarity * 100, 95)
            else:
                confidence = 0.0
            
            return {
                "answer": answer.strip(),
                "sources": sources,
                "confidence": round(confidence, 1),
                "context_used": len(context_parts)
            }
        
        except Exception as e:
            logger.error(f"❌ Erreur génération RAG Groq: {e}")
            return {
                "answer": f"Erreur lors de la génération de la réponse: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "context_used": 0
            }
    
    def generate_general_response(self, query: str) -> Dict:
        """Génère une réponse générale avec Groq"""
        system_prompt = """Tu es un assistant IA intelligent et serviable.

Règles importantes:
- Réponds avec ta connaissance générale
- Si la question nécessite des informations en temps réel (météo, actualités récentes, bourse), 
  explique clairement que tu n'as pas accès à ces données
- Si tu n'es pas sûr d'une information, dis-le honnêtement
- Sois précis, concis et structuré dans tes réponses
- Utilise un ton professionnel mais accessible"""

        user_prompt = f"""Question:
{query}

Réponds à cette question avec ta connaissance générale."""

        try:
            answer = self.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            return {
                "answer": answer.strip(),
                "sources": [],
                "confidence": 80.0,
                "context_used": 0
            }
        
        except Exception as e:
            logger.error(f"❌ Erreur génération réponse générale Groq: {e}")
            return {
                "answer": f"Erreur lors de la génération de la réponse: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "context_used": 0
            }


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory pour obtenir le bon provider LLM selon la config
    
    Returns:
        Instance du provider (Ollama ou Groq)
    """
    provider_type = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    if provider_type == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY manquante dans .env. "
                "Obtenez une clé sur: https://console.groq.com"
            )
        
        model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
        logger.info(f"🚀 Utilisation de Groq ({model})")
        
        return GroqProvider(api_key=api_key, model=model)
    
    else:  # ollama par défaut
        from ai.llm import LLMGenerator
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL")
        
        logger.info(f"🏠 Utilisation d'Ollama local ({base_url})")
        
        return LLMGenerator(base_url=base_url, model=model)


# Instance globale
_llm_provider = None

def get_llm_generator():
    """Retourne l'instance singleton du LLM provider"""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = get_llm_provider()
    return _llm_provider

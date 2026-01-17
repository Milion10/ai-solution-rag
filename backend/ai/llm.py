"""
Service de génération de texte avec LLM local via Ollama
Alternative simple à llama-cpp-python pour Windows
"""
import httpx
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class LLMGenerator:
    """
    Génère des réponses avec un LLM local via Ollama API
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        """
        Initialise le générateur LLM
        
        Args:
            base_url: URL de l'API Ollama
            model: Nom du modèle (auto-détecté si None)
            temperature: Contrôle la créativité (0.0-1.0)
            max_tokens: Nombre maximum de tokens générés
        """
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = httpx.Client(timeout=120.0)  # 2 min timeout pour génération
        
        # Auto-détection du modèle si non spécifié
        if model is None:
            model = self._detect_model()
        
        self.model = model
        logger.info(f"LLMGenerator initialisé: {model} @ {base_url}")
    
    
    def _detect_model(self) -> str:
        """Détecte automatiquement le premier modèle Mistral/Llama disponible"""
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    # Priorité: mistral > llama > premier dispo
                    for model in models:
                        name = model["name"]
                        if "mistral" in name.lower():
                            logger.info(f"✅ Modèle Mistral détecté: {name}")
                            return name
                    
                    for model in models:
                        name = model["name"]
                        if "llama" in name.lower():
                            logger.info(f"✅ Modèle Llama détecté: {name}")
                            return name
                    
                    # Prendre le premier disponible
                    first_model = models[0]["name"]
                    logger.info(f"✅ Modèle détecté: {first_model}")
                    return first_model
        except Exception as e:
            logger.warning(f"Impossible de détecter le modèle: {e}")
        
        # Fallback par défaut
        return "mistral:7b-instruct"
    
    
    def check_health(self) -> bool:
        """Vérifie si Ollama est disponible"""
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama non disponible: {e}")
            return False
    
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Génère une réponse à partir d'un prompt
        
        Args:
            prompt: Question ou instruction utilisateur
            system_prompt: Instructions système optionnelles
            temperature: Override température par défaut
            max_tokens: Override max_tokens par défaut
        
        Returns:
            Texte généré par le LLM
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature or self.temperature,
                "num_predict": max_tokens or self.max_tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            logger.info(f"🤖 Génération avec {self.model}...")
            
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "")
            
            logger.info(f"✅ Réponse générée: {len(generated_text)} caractères")
            
            return generated_text
        
        except Exception as e:
            logger.error(f"❌ Erreur génération LLM: {e}")
            raise
    
    
    def generate_rag_response(
        self,
        query: str,
        context_chunks: List[Dict],
        max_context_length: int = 3000
    ) -> Dict:
        """
        Génère une réponse RAG (Retrieval Augmented Generation)
        
        Args:
            query: Question utilisateur
            context_chunks: Chunks récupérés de la recherche vectorielle
            max_context_length: Longueur max du contexte (en caractères)
        
        Returns:
            Dict avec 'answer', 'sources', 'confidence'
        """
        # 1. Construire le contexte à partir des chunks
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
        
        # 2. Construire le prompt RAG
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
                temperature=0.3  # Faible température pour réponses factuelles
            )
            
            # 4. Estimer la confiance basée sur les scores de similarité
            if context_chunks:
                avg_similarity = sum(c["similarity"] for c in context_chunks[:3]) / min(3, len(context_chunks))
                confidence = min(avg_similarity * 100, 95)  # Cap à 95%
            else:
                confidence = 0.0
            
            return {
                "answer": answer.strip(),
                "sources": sources,
                "confidence": round(confidence, 1),
                "context_used": len(context_parts)
            }
        
        except Exception as e:
            logger.error(f"❌ Erreur génération RAG: {e}")
            return {
                "answer": f"Erreur lors de la génération de la réponse: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "context_used": 0
            }
    
    
    def generate_general_response(
        self,
        query: str
    ) -> Dict:
        """
        Génère une réponse avec la connaissance générale du modèle (sans RAG)
        Utilisé quand aucun document pertinent n'est trouvé
        
        Args:
            query: Question utilisateur
        
        Returns:
            Dict avec 'answer', 'sources', 'confidence'
        """
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
                temperature=0.7  # Température normale pour réponses générales
            )
            
            return {
                "answer": answer.strip(),
                "sources": [],  # Pas de sources pour la connaissance générale
                "confidence": 80.0,  # Confiance modérée (pas de docs pour vérifier)
                "context_used": 0
            }
        
        except Exception as e:
            logger.error(f"❌ Erreur génération réponse générale: {e}")
            return {
                "answer": f"Erreur lors de la génération de la réponse: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "context_used": 0
            }


# Instance globale
_llm_instance = None

def get_llm_generator() -> LLMGenerator:
    """Retourne l'instance singleton du LLM generator"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMGenerator()
    return _llm_instance


if __name__ == "__main__":
    # Test du LLM
    llm = LLMGenerator()
    
    print(f"\n🤖 LLMGenerator initialisé")
    print(f"📊 Modèle: {llm.model}")
    
    # Test santé
    if llm.check_health():
        print(f"✅ Ollama disponible")
        
        # Test génération simple
        response = llm.generate("Dis bonjour en français")
        print(f"\n💬 Test génération:")
        print(f"   {response[:100]}...")
    else:
        print(f"❌ Ollama non disponible")
        print(f"💡 Installez Ollama: https://ollama.ai")
        print(f"💡 Puis: ollama pull mistral:7b-instruct")

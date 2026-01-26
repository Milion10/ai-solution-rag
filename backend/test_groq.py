"""
Script de test pour vérifier la configuration Groq
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai.llm_factory import get_llm_generator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_groq_setup():
    """Teste la configuration et la connexion Groq"""
    print("\n" + "="*60)
    print("🧪 TEST CONFIGURATION GROQ")
    print("="*60)
    
    try:
        # 1. Récupérer le provider
        print("\n1️⃣ Initialisation du provider LLM...")
        llm = get_llm_generator()
        print(f"✅ Provider initialisé: {llm.__class__.__name__}")
        
        # 2. Vérifier la santé
        print("\n2️⃣ Vérification de la connexion...")
        if llm.check_health():
            print("✅ Groq API accessible")
        else:
            print("❌ Groq API non accessible")
            return False
        
        # 3. Test de génération simple
        print("\n3️⃣ Test de génération simple...")
        prompt = "Explique en une phrase ce qu'est le RAG."
        print(f"📝 Prompt: {prompt}")
        
        response = llm.generate(prompt=prompt, max_tokens=100)
        print(f"✅ Réponse reçue ({len(response)} caractères):")
        print(f"   {response[:200]}...")
        
        # 4. Test RAG (simulé)
        print("\n4️⃣ Test de génération RAG...")
        mock_chunks = [
            {
                "filename": "doc_test.txt",
                "content": "Le RAG (Retrieval-Augmented Generation) est une technique qui combine la recherche d'information et la génération de texte.",
                "chunk_index": 0,
                "similarity": 0.85
            }
        ]
        
        rag_response = llm.generate_rag_response(
            query="Qu'est-ce que le RAG ?",
            context_chunks=mock_chunks
        )
        
        print(f"✅ Réponse RAG générée:")
        print(f"   Answer: {rag_response['answer'][:200]}...")
        print(f"   Confidence: {rag_response['confidence']}%")
        print(f"   Sources: {len(rag_response['sources'])}")
        
        # 5. Test réponse générale
        print("\n5️⃣ Test de réponse générale...")
        gen_response = llm.generate_general_response(
            query="Quelle est la capitale de la France ?"
        )
        
        print(f"✅ Réponse générale:")
        print(f"   {gen_response['answer'][:200]}...")
        
        print("\n" + "="*60)
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("="*60)
        print("\n💡 Groq est opérationnel. Le backend devrait maintenant répondre en <2 secondes.")
        print("   Pour retourner à Ollama en production, changez LLM_PROVIDER=ollama dans .env\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_groq_setup()
    sys.exit(0 if success else 1)

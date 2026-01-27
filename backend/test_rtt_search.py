# encoding: utf-8
"""
Script simplifié pour tester la recherche RTT
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai.vector_store import get_vector_store
from ai.embeddings import EmbeddingsGenerator


def test_rtt_search():
    """Test la recherche de RTT avec différentes requêtes"""
    
    print("\n" + "="*80)
    print("TEST RECHERCHE RTT")
    print("="*80)
    
    vector_store = get_vector_store()
    
    # Différentes formulations de la requête
    queries = [
        "j'ai le droit a des rtt ?",
        "ai-je droit aux RTT ?",
        "puis-je avoir des jours de reduction du temps de travail ?",
        "comment fonctionnent les RTT ?",
        "RTT à Villeurbanne",
    ]
    
    print("\nTest avec différentes formulations:\n")
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"Requete: '{query}'")
        print(f"{'='*80}")
        
        # Rechercher avec seuil très bas pour voir tous les résultats
        chunks = vector_store.search_similar(
            query_text=query,
            top_k=5,
            similarity_threshold=0.0,  # Récupérer TOUS les chunks
            user_id=None,
            organization_id=None
        )
        
        if not chunks:
            print("  Aucun chunk trouvé (base vide?)")
            continue
        
        print(f"\n  Top 5 chunks:")
        for idx, chunk in enumerate(chunks[:5], 1):
            similarity = chunk['similarity']
            filename = chunk['filename']
            content_preview = chunk['content'][:80]
            
            status = "OK" if similarity >= 0.4 else "TROP BAS"
            symbol = "[+]" if similarity >= 0.4 else "[X]"
            
            print(f"\n  {symbol} #{idx}: {similarity:.4f} ({similarity*100:.1f}%) - {status}")
            print(f"      Fichier: {filename}")
            print(f"      Contenu: {content_preview}...")
    
    print("\n" + "="*80)
    print("CONCLUSIONS:")
    print("="*80)
    print("""
Si les scores sont < 0.4 (40%):
  PROBLEME: Le modèle d'embedding ne comprend pas bien 'RTT'
  
  SOLUTIONS:
  1. Baisser le seuil dans backend/api/chat.py:
     Ligne 92: RELEVANCE_THRESHOLD = 0.4  =>  0.3
  
  2. Reformuler la question:
     Au lieu de: "j'ai le droit a des rtt ?"
     Utiliser: "comment fonctionnent les jours de récupération RTT ?"
  
  3. Améliorer le chunking pour mieux capturer le contexte RTT
  
  4. Utiliser un meilleur modèle d'embedding multilingue
     Remplacer: all-MiniLM-L6-v2
     Par: paraphrase-multilingual-MiniLM-L12-v2
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    test_rtt_search()

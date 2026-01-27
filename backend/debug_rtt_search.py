# encoding: utf-8
"""
Verifier la similarite exacte des chunks RTT
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai.vector_store import get_vector_store

def test_specific_chunks():
    """Teste la similarite pour tous les chunks du Guide"""
    
    print("\n" + "="*80)
    print("RECHERCHE VECTORIELLE - TOUS LES CHUNKS")
    print("="*80)
    
    vector_store = get_vector_store()
    
    query = "j'ai le droit a des rtt ?"
    print(f"\nRequete: '{query}'")
    
    # Recuperer BEAUCOUP de chunks (top 20) avec seuil 0
    chunks = vector_store.search_similar(
        query_text=query,
        top_k=20,
        similarity_threshold=0.0,
        user_id=None,
        organization_id=None
    )
    
    print(f"\nTop 20 chunks retournes:\n")
    
    # Chercher specifiquement les chunks du Guide qui parlent de RTT
    guide_chunks = [c for c in chunks if 'Guide_Conges' in c['filename']]
    
    for idx, chunk in enumerate(chunks[:20], 1):
        similarity = chunk['similarity']
        filename = chunk['filename'].replace('_WEB', '')
        chunk_idx = chunk['chunk_index']
        preview = chunk['content'][:60].replace('\n', ' ')
        
        # Highlighter les chunks 3 et 6 du Guide
        highlight = ""
        if 'Guide_Conges' in filename and chunk_idx in [3, 4, 6, 7]:
            highlight = " <--- CHUNK AVEC EXPLICATION RTT !!!"
        
        symbol = "[+]" if similarity >= 0.35 else "[X]"
        
        print(f"{symbol} #{idx}: {similarity:.4f} ({similarity*100:.1f}%) | "
              f"{filename[:30]:30} chunk#{chunk_idx:2} | {preview}...{highlight}")
    
    print("\n" + "="*80)
    print("PROBLEME IDENTIFIE:")
    print("="*80)
    print("""
Les chunks 3, 4, 6, 7 du Guide contiennent l'explication des RTT
mais ils n'apparaissent PAS dans le top 10 des resultats !

Leur score de similarite est trop BAS par rapport aux autres chunks.

POURQUOI ?
Le modele d'embedding 'all-MiniLM-L6-v2' ne comprend pas bien
l'acronyme 'RTT' en français.

SOLUTIONS:
1. Utiliser un modele multilingue meilleur
2. Ajouter des synonymes dans la requete
3. Reindexer avec un meilleur modele
    """)
    print("="*80 + "\n")

if __name__ == "__main__":
    test_specific_chunks()

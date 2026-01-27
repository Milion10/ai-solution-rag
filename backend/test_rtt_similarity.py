# encoding: utf-8
"""
Script pour analyser la similarité des chunks RTT
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import SessionLocal
from sqlalchemy import text
from ai.embeddings import EmbeddingsGenerator
import numpy as np
from numpy import dot
from numpy.linalg import norm


def analyze_similarity():
    """Analyse la similarité entre la requête et les chunks RTT"""
    
    print("\n" + "="*80)
    print("ANALYSE SIMILARITE RTT")
    print("="*80)
    
    with SessionLocal() as db:
        # Requête utilisateur
        user_query = "j'ai le droit a des rtt ?"
        print(f"\nRequete: '{user_query}'")
        
        # Générer embedding
        embedding_model = EmbeddingsGenerator()
        query_embedding = embedding_model.generate_embedding(user_query)
        print(f"Embedding genere: {len(query_embedding)} dimensions\n")
        
        # Récupérer les chunks RTT
        query = text("""
            SELECT 
                d.filename,
                dc.chunk_index,
                dc.embedding,
                SUBSTRING(dc.content, 1, 100) as preview
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE LOWER(dc.content) LIKE '%rtt%'
            ORDER BY d.filename, dc.chunk_index
            LIMIT 10
        """)
        
        results = db.execute(query).fetchall()
        
        print(f"Chunks trouvés: {len(results)}\n")
        print("="*80)
        print("SCORES DE SIMILARITE:")
        print("="*80)
        
        for idx, row in enumerate(results, 1):
            filename = row[0]
            chunk_index = row[1]
            chunk_embedding = row[2]
            preview = row[3]
            
            # Convertir embedding
            if isinstance(chunk_embedding, str):
                chunk_embedding = chunk_embedding.strip('{}').split(',')
                chunk_embedding = [float(x) for x in chunk_embedding]
            
            query_vec = np.array(query_embedding, dtype=float)
            chunk_vec = np.array(chunk_embedding, dtype=float)
            
            # Similarité cosine
            similarity = dot(query_vec, chunk_vec) / (norm(query_vec) * norm(chunk_vec))
            
            status = "OK" if similarity >= 0.4 else "TROP BAS"
            symbol = "[+]" if similarity >= 0.4 else "[X]"
            
            print(f"\n{symbol} Chunk {idx}: {similarity:.4f} ({similarity*100:.1f}%) - {status}")
            print(f"    Fichier: {filename}")
            print(f"    Index: {chunk_index}")
            print(f"    Preview: {preview}...")
        
        print("\n" + "="*80)
        print("DIAGNOSTIC:")
        print("="*80)
        
        above_threshold = sum(1 for row in results if True)  # Calculer après
        print(f"\nSeuil actuel: 0.4 (40%)")
        print(f"Chunks au-dessus du seuil: ? / {len(results)}")
        print("\nSi aucun chunk n'est au-dessus de 0.4:")
        print("  1. Le modele d'embedding ne comprend pas bien 'RTT'")
        print("  2. Solution: Reformuler la question")
        print("  3. Ou: Baisser le seuil a 0.3 dans chat.py (ligne 92)")
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    analyze_similarity()

"""
Script pour analyser pourquoi les RTT ne sont pas trouvés
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import SessionLocal
from sqlalchemy import text
from ai.embeddings import EmbeddingsGenerator


def analyze_rtt_in_documents():
    """Analyse les documents pour trouver les mentions de RTT"""
    
    print("\n" + "="*100)
    print("🔍 ANALYSE DES RTT DANS LES DOCUMENTS")
    print("="*100)
    
    with SessionLocal() as db:
        # 1. Trouver tous les chunks qui contiennent "RTT" (case insensitive)
        query = text("""
            SELECT 
                d.filename,
                dc.chunk_index,
                dc.content,
                LENGTH(dc.content) as content_length
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE LOWER(dc.content) LIKE '%rtt%'
            OR LOWER(dc.content) LIKE '%réduction du temps de travail%'
            OR LOWER(dc.content) LIKE '%reduction du temps%'
            ORDER BY d.filename, dc.chunk_index
        """)
        
        results = db.execute(query).fetchall()
        
        if not results:
            print("\n❌ Aucun chunk contenant 'RTT' ou 'réduction du temps de travail' trouvé")
            print("   → Le document n'a peut-être pas été indexé correctement")
            return
        
        print(f"\n✅ {len(results)} chunk(s) contenant des mentions de RTT trouvés\n")
        
        for idx, row in enumerate(results, 1):
            filename = row[0]
            chunk_index = row[1]
            content = row[2]
            length = row[3]
            
            print(f"{'─'*100}")
            print(f"📄 Chunk #{idx}")
            print(f"{'─'*100}")
            print(f"  Fichier:      {filename}")
            print(f"  Chunk index:  {chunk_index}")
            print(f"  Longueur:     {length} caractères")
            print(f"\n  Contenu (extrait):")
            print(f"  {'-'*96}")
            # Afficher les 500 premiers caractères
            preview = content[:500] + "..." if len(content) > 500 else content
            print(f"  {preview}")
            print(f"  {'-'*96}\n")
        
        # 2. Tester la similarité avec la requête utilisateur
        print("\n" + "="*100)
        print("🧪 TEST DE SIMILARITÉ AVEC LA REQUÊTE")
        print("="*100)
        
        user_query = "j'ai le droit a des rtt ?"
        print(f"\nRequête utilisateur: '{user_query}'")
        
        # Générer l'embedding de la requête
        embedding_model = EmbeddingsGenerator()
        query_embedding = embedding_model.generate_embedding(user_query)
        
        print(f"Embedding généré: {len(query_embedding)} dimensions\n")
        
        # Calculer la similarité avec chaque chunk trouvé
        print("Similarités avec les chunks contenant 'RTT':")
        print(f"{'─'*100}")
        
        for idx, row in enumerate(results, 1):
            filename = row[0]
            chunk_index = row[1]
            
            # Récupérer l'embedding du chunk
            embed_query = text("""
                SELECT embedding
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.filename = :filename AND dc.chunk_index = :chunk_index
            """)
            
            embed_result = db.execute(embed_query, {
                "filename": filename,
                "chunk_index": chunk_index
            }).fetchone()
            
            if embed_result and embed_result[0]:
                chunk_embedding = embed_result[0]
                
                # Convertir les embeddings en numpy arrays si ce sont des strings
                import numpy as np
                from numpy import dot
                from numpy.linalg import norm
                
                # Convertir les embeddings (peuvent être stockés comme des listes)
                if isinstance(chunk_embedding, str):
                    # Si c'est un string PostgreSQL array, le parser
                    chunk_embedding = chunk_embedding.strip('{}').split(',')
                    chunk_embedding = [float(x) for x in chunk_embedding]
                
                query_vec = np.array(query_embedding, dtype=float)
                chunk_vec = np.array(chunk_embedding, dtype=float)
                
                # Calculer la similarité cosine
                similarity = dot(query_vec, chunk_vec) / (norm(query_vec) * norm(chunk_vec))
                
                print(f"  Chunk {idx} ({filename}, index {chunk_index}): {similarity:.4f} ({similarity*100:.2f}%)")
                
                if similarity < 0.4:
                    print(f"    ⚠️  En dessous du seuil de 0.4 (40%) → Ne sera PAS récupéré par le RAG")
                else:
                    print(f"    ✅ Au-dessus du seuil → Sera récupéré par le RAG")
        
        print(f"{'─'*100}\n")
        
        # 3. Recommandations
        print("\n" + "="*100)
        print("💡 RECOMMANDATIONS")
        print("="*100)
        
        print("""
1. Si la similarité est faible (<0.4):
   - Le modèle d'embedding ne comprend pas bien 'RTT'
   - Solution: Améliorer la requête (ex: "ai-je droit à la réduction du temps de travail?")
   - Ou: Baisser le seuil de similarité dans le code (actuellement 0.4)

2. Si les chunks sont mal découpés:
   - Ajuster les paramètres de chunking (size, overlap)
   - Actuellement: size=800, overlap=200

3. Si le contenu n'est pas trouvé:
   - Vérifier que le PDF a bien été indexé
   - Réindexer le document si nécessaire
        """)
        print("="*100 + "\n")


if __name__ == "__main__":
    analyze_rtt_in_documents()

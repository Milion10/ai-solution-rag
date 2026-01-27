# encoding: utf-8
"""
Vérifier le contenu exact des chunks RTT
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import SessionLocal
from sqlalchemy import text


def check_rtt_content():
    """Affiche le contenu complet des chunks contenant RTT"""
    
    print("\n" + "="*80)
    print("CONTENU DES CHUNKS RTT")
    print("="*80)
    
    with SessionLocal() as db:
        query = text("""
            SELECT 
                d.filename,
                dc.chunk_index,
                dc.content
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE LOWER(dc.content) LIKE '%jours de rtt%'
               OR LOWER(dc.content) LIKE '%reduction du temps de travail%'
               OR (LOWER(dc.content) LIKE '%rtt%' AND LOWER(dc.content) LIKE '%vous avez droit%')
            ORDER BY d.filename, dc.chunk_index
            LIMIT 5
        """)
        
        results = db.execute(query).fetchall()
        
        if not results:
            print("\nAucun chunk trouve avec explication RTT")
            return
        
        print(f"\n{len(results)} chunks trouves\n")
        
        for idx, row in enumerate(results, 1):
            filename = row[0]
            chunk_index = row[1]
            content = row[2]
            
            print(f"\n{'='*80}")
            print(f"CHUNK #{idx}")
            print(f"{'='*80}")
            print(f"Fichier: {filename}")
            print(f"Index: {chunk_index}")
            print(f"\nCONTENU COMPLET:")
            print("-"*80)
            print(content)
            print("-"*80)
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    check_rtt_content()

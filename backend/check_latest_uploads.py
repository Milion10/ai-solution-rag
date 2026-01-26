"""
Script pour vérifier les derniers uploads en base
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from utils.database import SessionLocal
from datetime import datetime, timedelta

def check_latest_uploads():
    """Vérifie les derniers uploads (dernières 5 minutes)"""
    with SessionLocal() as db:
        # Documents des 5 dernières minutes
        query = text("""
            SELECT 
                filename,
                scope,
                conversation_id,
                is_indexed,
                indexing_status,
                uploaded_at,
                (SELECT COUNT(*) FROM document_chunks WHERE document_id = d.id) as chunk_count
            FROM documents d
            WHERE uploaded_at > NOW() - INTERVAL '5 minutes'
            ORDER BY uploaded_at DESC
        """)
        
        result = db.execute(query)
        docs = result.fetchall()
        
        if not docs:
            print("❌ Aucun document uploadé dans les 5 dernières minutes")
            return
        
        print(f"\n✅ {len(docs)} document(s) uploadé(s) dans les 5 dernières minutes:\n")
        
        for doc in docs:
            print(f"📄 {doc[0]}")
            print(f"   Scope: {doc[1]}")
            print(f"   Conversation ID: {doc[2] or '❌ AUCUN'}")
            print(f"   Indexé: {'✅' if doc[3] else '❌'}")
            print(f"   Status: {doc[4]}")
            print(f"   Chunks: {doc[6]}")
            print(f"   Uploadé: {doc[5]}")
            print()

if __name__ == "__main__":
    check_latest_uploads()

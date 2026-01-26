"""
Debug complet du flux d'upload et recherche
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import SessionLocal
from sqlalchemy import text


def check_recent_uploads():
    """Vérifie les uploads récents et leurs attributs"""
    
    print("\n" + "="*80)
    print("🔍 DOCUMENTS RÉCENTS (dernières 24h)")
    print("="*80)
    
    with SessionLocal() as db:
        query = text("""
            SELECT 
                filename,
                scope,
                conversation_id,
                is_indexed,
                uploaded_at,
                indexing_status,
                (SELECT COUNT(*) FROM document_chunks WHERE document_id = documents.id) as chunk_count
            FROM documents
            WHERE uploaded_at > NOW() - INTERVAL '24 hours'
            ORDER BY uploaded_at DESC
        """)
        
        results = db.execute(query).fetchall()
        
        if not results:
            print("\n❌ Aucun document récent")
            return
        
        for doc in results:
            print(f"\n📄 {doc[0]}")
            print(f"   Scope: {doc[1]}")
            print(f"   Conversation ID: {doc[2] or '❌ AUCUN'}")
            print(f"   Indexé: {'✅' if doc[3] else '❌'}")
            print(f"   Status: {doc[5]}")
            print(f"   Chunks: {doc[6]}")
            print(f"   Date: {doc[4]}")


def check_conversations():
    """Liste les conversations actives"""
    
    print("\n" + "="*80)
    print("💬 CONVERSATIONS ACTIVES")
    print("="*80)
    
    with SessionLocal() as db:
        query = text("""
            SELECT 
                id,
                title,
                created_at,
                (SELECT COUNT(*) FROM documents WHERE conversation_id = conversations.id) as doc_count
            FROM conversations
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        try:
            results = db.execute(query).fetchall()
            
            if not results:
                print("\n⚠️ Aucune conversation trouvée")
                return
            
            for conv in results:
                print(f"\n🗨️ {conv[1] or 'Sans titre'}")
                print(f"   ID: {conv[0]}")
                print(f"   Documents: {conv[3]}")
                print(f"   Créée: {conv[2]}")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")


def test_search_current_conversation():
    """Teste la recherche dans la conversation la plus récente"""
    
    print("\n" + "="*80)
    print("🧪 TEST RECHERCHE DANS CONVERSATION RÉCENTE")
    print("="*80)
    
    with SessionLocal() as db:
        # Récupérer la conversation la plus récente qui a des documents
        query = text("""
            SELECT DISTINCT d.conversation_id
            FROM documents d
            WHERE d.conversation_id IS NOT NULL
              AND d.is_indexed = true
            ORDER BY d.uploaded_at DESC
            LIMIT 1
        """)
        
        result = db.execute(query).fetchone()
        
        if not result or not result[0]:
            print("\n❌ Aucune conversation avec documents indexés")
            return
        
        conv_id = result[0]
        print(f"\n🔑 Conversation ID: {conv_id}")
        
        # Compter les documents de cette conversation
        count_query = text("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE conversation_id = :conv_id AND is_indexed = true
        """)
        count = db.execute(count_query, {"conv_id": conv_id}).scalar()
        print(f"📄 Documents indexés dans cette conv: {count}")
        
        # Lister les documents
        docs_query = text("""
            SELECT filename, 
                   (SELECT COUNT(*) FROM document_chunks WHERE document_id = documents.id) as chunks
            FROM documents 
            WHERE conversation_id = :conv_id
        """)
        docs = db.execute(docs_query, {"conv_id": conv_id}).fetchall()
        
        for doc in docs:
            print(f"   - {doc[0]} ({doc[1]} chunks)")
    
    # Test de recherche
    from ai.vector_store import get_vector_store
    
    print("\n🔍 Test recherche avec conversation_id...")
    vector_store = get_vector_store()
    
    results = vector_store.search_similar(
        query_text="projet ingénieur",
        top_k=5,
        similarity_threshold=0.0,
        user_id=None,
        organization_id=None,
        conversation_id=conv_id
    )
    
    print(f"   Résultats: {len(results)}")
    for r in results[:3]:
        print(f"   - {r['filename']} (sim: {r['similarity']:.2f}, scope: {r.get('scope', 'N/A')})")


if __name__ == "__main__":
    check_recent_uploads()
    check_conversations()
    test_search_current_conversation()
    print("\n" + "="*80 + "\n")

"""
Script de debug pour vérifier les documents avec conversation_id
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import SessionLocal
from sqlalchemy import text


def debug_documents():
    """Liste tous les documents en base avec leurs attributs"""
    
    print("\n" + "="*80)
    print("🔍 DEBUG: Documents en base de données")
    print("="*80)
    
    with SessionLocal() as db:
        # Récupérer tous les documents
        query = text("""
            SELECT 
                id,
                filename,
                scope,
                user_id,
                organization_id,
                conversation_id,
                is_indexed,
                uploaded_at
            FROM documents
            ORDER BY uploaded_at DESC
            LIMIT 20
        """)
        
        result = db.execute(query)
        documents = result.fetchall()
        
        if not documents:
            print("\n❌ Aucun document trouvé en base")
            return
        
        print(f"\n📄 {len(documents)} documents trouvés:\n")
        
        for doc in documents:
            print(f"📌 {doc[1]}")  # filename
            print(f"   ID: {str(doc[0])[:8]}...")
            print(f"   Scope: {doc[2]}")
            print(f"   User ID: {doc[3] or 'N/A'}")
            print(f"   Org ID: {doc[4] or 'N/A'}")
            print(f"   Conv ID: {doc[5] or 'N/A'}")  # ← IMPORTANT
            print(f"   Indexé: {'✅' if doc[6] else '❌'}")
            print(f"   Date: {doc[7]}")
            print()
        
        # Compter par type
        count_query = text("""
            SELECT 
                CASE 
                    WHEN conversation_id IS NOT NULL THEN 'conversation'
                    WHEN scope = 'organization' THEN 'organization'
                    WHEN scope = 'user' THEN 'user'
                    ELSE 'other'
                END as type,
                COUNT(*) as count
            FROM documents
            GROUP BY type
        """)
        
        counts = db.execute(count_query).fetchall()
        
        print("📊 Répartition:")
        for type_name, count in counts:
            print(f"   {type_name}: {count}")


def test_search_with_conversation():
    """Teste une recherche avec conversation_id"""
    
    print("\n" + "="*80)
    print("🧪 TEST: Recherche avec conversation_id")
    print("="*80)
    
    from ai.vector_store import get_vector_store
    
    # Récupérer un conversation_id de test depuis la base
    with SessionLocal() as db:
        query = text("""
            SELECT DISTINCT conversation_id 
            FROM documents 
            WHERE conversation_id IS NOT NULL 
            LIMIT 1
        """)
        result = db.execute(query).fetchone()
        
        if not result or not result[0]:
            print("\n⚠️ Aucun document avec conversation_id trouvé")
            return
        
        test_conv_id = result[0]
        print(f"\n🔑 Test avec conversation_id: {test_conv_id}")
    
    # Test de recherche
    vector_store = get_vector_store()
    
    # Recherche SANS conversation_id
    print("\n1️⃣ Recherche SANS conversation_id...")
    results_without = vector_store.search_similar(
        query_text="projet ingénieur",
        top_k=5,
        similarity_threshold=0.0,
        user_id=None,
        organization_id=None,
        conversation_id=None
    )
    print(f"   Résultats: {len(results_without)}")
    
    # Recherche AVEC conversation_id
    print("\n2️⃣ Recherche AVEC conversation_id...")
    results_with = vector_store.search_similar(
        query_text="projet ingénieur",
        top_k=5,
        similarity_threshold=0.0,
        user_id=None,
        organization_id=None,
        conversation_id=test_conv_id
    )
    print(f"   Résultats: {len(results_with)}")
    
    if results_with:
        print("\n   📚 Documents trouvés:")
        for r in results_with[:3]:
            print(f"      - {r['filename']} (similarité: {r['similarity']:.2f})")


if __name__ == "__main__":
    debug_documents()
    test_search_with_conversation()
    print("\n" + "="*80 + "\n")

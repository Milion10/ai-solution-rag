"""
Script pour vérifier tous les documents en base de données
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import SessionLocal
from sqlalchemy import text


def check_all_documents():
    """Affiche tous les documents avec leurs attributs"""
    
    print("\n" + "="*100)
    print("📊 TOUS LES DOCUMENTS EN BASE DE DONNÉES")
    print("="*100)
    
    with SessionLocal() as db:
        query = text("""
            SELECT 
                id,
                filename,
                scope,
                user_id,
                organization_id,
                conversation_id,
                uploaded_at,
                is_indexed
            FROM documents
            ORDER BY uploaded_at DESC
        """)
        
        results = db.execute(query).fetchall()
        
        if not results:
            print("\n❌ Aucun document trouvé en base")
            return
        
        print(f"\n✅ {len(results)} document(s) trouvé(s)\n")
        
        for idx, row in enumerate(results, 1):
            doc_id = row[0]
            filename = row[1]
            scope = row[2]
            user_id = row[3]
            org_id = row[4]
            conv_id = row[5]
            uploaded_at = row[6]
            is_indexed = row[7]
            
            print(f"{'─'*100}")
            print(f"📄 Document #{idx}")
            print(f"{'─'*100}")
            print(f"  ID:              {doc_id}")
            print(f"  Filename:        {filename}")
            print(f"  📌 Scope:        {scope}")
            print(f"  👤 User ID:      {user_id}")
            print(f"  🏢 Org ID:       {org_id}")
            print(f"  💬 Conv ID:      {conv_id}")
            print(f"  📅 Uploaded:     {uploaded_at}")
            print(f"  🔍 Indexed:      {is_indexed}")
            
            # Analyse du scope
            if scope == "user":
                print(f"  ℹ️  Type:         Document PERSONNEL")
            elif scope == "organization":
                print(f"  ℹ️  Type:         Document GLOBAL (Organisation)")
            elif scope == "conversation":
                print(f"  ℹ️  Type:         Document de CONVERSATION")
            else:
                print(f"  ⚠️  Type:         SCOPE INCONNU!")
            
            # Vérifications
            if scope == "organization" and not org_id:
                print(f"  ⚠️  PROBLÈME:     Document organization SANS organization_id!")
            
            if scope == "user" and not user_id:
                print(f"  ⚠️  PROBLÈME:     Document user SANS user_id!")
            
            if scope == "conversation" and not conv_id:
                print(f"  ⚠️  PROBLÈME:     Document conversation SANS conversation_id!")
            
            print()


def check_specific_document(filename: str):
    """Vérifie un document spécifique par son nom"""
    
    print("\n" + "="*100)
    print(f"🔍 RECHERCHE DU DOCUMENT: {filename}")
    print("="*100)
    
    with SessionLocal() as db:
        query = text("""
            SELECT 
                id,
                filename,
                scope,
                user_id,
                organization_id,
                conversation_id,
                uploaded_at,
                is_indexed
            FROM documents
            WHERE filename = :filename
        """)
        
        result = db.execute(query, {"filename": filename}).fetchone()
        
        if not result:
            print(f"\n❌ Document '{filename}' non trouvé en base")
            return
        
        doc_id = result[0]
        filename = result[1]
        scope = result[2]
        user_id = result[3]
        org_id = result[4]
        conv_id = result[5]
        uploaded_at = result[6]
        is_indexed = result[7]
        
        print(f"\n✅ Document trouvé !\n")
        print(f"{'─'*100}")
        print(f"  ID:              {doc_id}")
        print(f"  Filename:        {filename}")
        print(f"  📌 Scope:        {scope}")
        print(f"  👤 User ID:      {user_id}")
        print(f"  🏢 Org ID:       {org_id}")
        print(f"  💬 Conv ID:      {conv_id}")
        print(f"  📅 Uploaded:     {uploaded_at}")
        print(f"  🔍 Indexed:      {is_indexed}")
        print(f"{'─'*100}")
        
        # Analyse du scope
        print(f"\n📊 ANALYSE:")
        if scope == "user":
            print(f"  ✓ Type:         Document PERSONNEL")
            print(f"  ✓ Suppression:  Seul le propriétaire (user_id={user_id}) peut supprimer")
        elif scope == "organization":
            print(f"  ✓ Type:         Document GLOBAL (Organisation)")
            print(f"  ✓ Suppression:  Seul un ADMIN peut supprimer")
            if not org_id:
                print(f"  ⚠️  ATTENTION:   organization_id est NULL! C'est peut-être le problème!")
        elif scope == "conversation":
            print(f"  ✓ Type:         Document de CONVERSATION")
            print(f"  ✓ Suppression:  Seul le propriétaire peut supprimer")
            print(f"  ⚠️  ATTENTION:   Ce document ne devrait PAS apparaître dans le dashboard global!")
        else:
            print(f"  ❌ Type:        SCOPE INCONNU: '{scope}'")
        
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Vérifier les documents en base")
    parser.add_argument("--file", "-f", help="Nom du fichier à rechercher", default=None)
    args = parser.parse_args()
    
    if args.file:
        check_specific_document(args.file)
    else:
        check_all_documents()
    
    print("="*100 + "\n")

"""
Script pour supprimer TOUS les documents de la base de données
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import SessionLocal
from sqlalchemy import text
from pathlib import Path


def delete_all_documents():
    """Supprime tous les documents de la base et du disque"""
    
    print("\n" + "="*80)
    print("⚠️  SUPPRESSION DE TOUS LES DOCUMENTS")
    print("="*80)
    
    with SessionLocal() as db:
        # Compter les documents
        count_query = text("SELECT COUNT(*) FROM documents")
        count = db.execute(count_query).scalar()
        
        print(f"\n📊 {count} document(s) trouvé(s) en base")
        
        if count == 0:
            print("✅ Aucun document à supprimer")
            return
        
        # Récupérer tous les filenames pour supprimer les fichiers du disque
        filenames_query = text("SELECT filename FROM documents")
        filenames = [row[0] for row in db.execute(filenames_query).fetchall()]
        
        print(f"\n🗑️  Suppression en cours...")
        
        # Supprimer tous les chunks (CASCADE devrait le faire mais soyons explicites)
        delete_chunks = text("DELETE FROM document_chunks")
        chunks_deleted = db.execute(delete_chunks).rowcount
        print(f"  ✓ {chunks_deleted} chunks supprimés")
        
        # Supprimer tous les documents
        delete_docs = text("DELETE FROM documents")
        docs_deleted = db.execute(delete_docs).rowcount
        print(f"  ✓ {docs_deleted} documents supprimés de la base")
        
        db.commit()
        
        print(f"\n📁 Suppression des fichiers du disque...")
        
        # Supprimer les fichiers du disque
        upload_dir = Path(__file__).parent / "uploads"
        deleted_files = 0
        not_found = 0
        
        for filename in filenames:
            file_path = upload_dir / filename
            if file_path.exists():
                try:
                    os.remove(file_path)
                    deleted_files += 1
                except Exception as e:
                    print(f"  ⚠️  Erreur suppression {filename}: {e}")
            else:
                not_found += 1
        
        print(f"  ✓ {deleted_files} fichier(s) supprimé(s) du disque")
        if not_found > 0:
            print(f"  ℹ️  {not_found} fichier(s) déjà absent(s) du disque")
        
        print(f"\n✅ Tous les documents ont été supprimés !")
        print("="*80 + "\n")


if __name__ == "__main__":
    # Demander confirmation
    print("\n⚠️  ATTENTION: Cette action va supprimer TOUS les documents !")
    print("   - Base de données: OUI")
    print("   - Fichiers disque: OUI")
    print("   - Cette action est IRRÉVERSIBLE")
    
    confirmation = input("\nTaper 'OUI' en majuscules pour confirmer: ")
    
    if confirmation == "OUI":
        delete_all_documents()
    else:
        print("\n❌ Suppression annulée")
        print("="*80 + "\n")

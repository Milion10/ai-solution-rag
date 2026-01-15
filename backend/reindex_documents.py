"""
Script pour ré-indexer les documents qui ne sont pas indexés
"""
import sys
from pathlib import Path
from sqlalchemy import text
from utils.database import SessionLocal
from ai.vector_store import VectorStore

def reindex_documents():
    vector_store = VectorStore()
    db = SessionLocal()
    try:
        # Récupérer tous les documents non indexés
        result = db.execute(text("""
            SELECT id, filename, file_path 
            FROM documents 
            WHERE is_indexed = false
        """))
        documents = result.fetchall()
        
        if not documents:
            print("✅ Aucun document à ré-indexer")
            return
        
        print(f"📄 {len(documents)} document(s) à ré-indexer")
        
        for doc in documents:
            doc_id, filename, file_path = doc
            print(f"\n🔄 Indexation de {filename}...")
            
            # Vérifier que le fichier existe
            if not Path(file_path).exists():
                print(f"❌ Fichier introuvable: {file_path}")
                continue
            
            # Lire le contenu du fichier
            try:
                import pypdf
                with open(file_path, 'rb') as f:
                    pdf_reader = pypdf.PdfReader(f)
                    text_content = ""
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"
            except Exception as e:
                print(f"❌ Erreur lecture PDF: {e}")
                continue
            
            # Indexer le document
            try:
                # Utiliser le document_id existant
                result = vector_store.store_document(
                    filename=filename,
                    content=text_content,
                    file_path=file_path,
                    file_type="application/pdf",
                    file_size=Path(file_path).stat().st_size,
                    user_id=None  # Ou récupérer le user_id de la DB si nécessaire
                )
                
                # Mettre à jour le document existant
                db.execute(text("""
                    UPDATE documents 
                    SET is_indexed = true, indexing_status = 'completed'
                    WHERE id = :doc_id
                """), {"doc_id": doc_id})
                db.commit()
                
                print(f"✅ {filename} indexé avec succès")
            except Exception as e:
                print(f"❌ Erreur indexation: {e}")
                db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Démarrage de la ré-indexation...\n")
    reindex_documents()
    print("\n✨ Ré-indexation terminée")

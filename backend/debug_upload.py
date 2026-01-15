"""
Script de debug pour tester l'upload + indexation directement
Sans passer par FastAPI
"""
import sys
from pathlib import Path
from ai.vector_store import get_vector_store

# Lire le PDF déjà uploadé
pdf_path = Path("uploads/prd-1.pdf")

if not pdf_path.exists():
    print(f"❌ PDF non trouvé: {pdf_path}")
    sys.exit(1)

# Extraire le texte
import pypdf

with open(pdf_path, "rb") as f:
    pdf_reader = pypdf.PdfReader(f)
    page_count = len(pdf_reader.pages)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"

print(f"📄 PDF lu: {pdf_path.name}")
print(f"   Pages: {page_count}")
print(f"   Caractères: {len(text)}")

# Tester le vector store
print("\n🚀 Test de l'indexation...")

try:
    vector_store = get_vector_store()
    print(f"✅ VectorStore initialisé (embedding dim: {vector_store.embedding_dim})")
    
    document_id = vector_store.store_document(
        filename=pdf_path.name,
        content=text,
        file_path=str(pdf_path),
        file_type="pdf",
        file_size=pdf_path.stat().st_size,
        page_count=page_count
    )
    
    print(f"\n✅ Document indexé avec succès!")
    print(f"   Document ID: {document_id}")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

"""
Test simple : Upload + Recherche
"""
import httpx
from pathlib import Path

API_URL = "http://localhost:8000"

print("🧪 Test RAG Simple\n")

# 1. Vérifier serveur
print("1. Vérification serveur...")
try:
    r = httpx.get(f"{API_URL}/health", timeout=5)
    print(f"   ✅ Serveur OK: {r.json()}\n")
except:
    print("   ❌ Serveur non accessible\n")
    exit(1)

# 2. Chercher PDF
pdf_path = Path("uploads/prd-1.pdf")
if not pdf_path.exists():
    print(f"   ⚠️  PDF non trouvé: {pdf_path}\n")
    exit(0)

print(f"2. Upload PDF: {pdf_path.name}")
print(f"   Taille: {pdf_path.stat().st_size // 1024} KB\n")

# 3. Upload avec indexation
with open(pdf_path, "rb") as f:
    files = {"file": (pdf_path.name, f, "application/pdf")}
    
    print("   ⏳ Upload + Indexation en cours...")
    r = httpx.post(
        f"{API_URL}/api/documents/upload?auto_index=true",
        files=files,
        timeout=300
    )
    
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ Succès!")
        print(f"      Pages: {data['page_count']}")
        print(f"      Texte: {data['text_length']} chars")
        print(f"      Indexé: {data.get('indexed', False)}")
        if data.get('indexed'):
            print(f"      Doc ID: {data['document_id'][:8]}...")
    else:
        print(f"   ❌ Erreur: {r.status_code}")
        print(f"      {r.text[:200]}")
        exit(1)

print("\n3. Tests de recherche...\n")

queries = [
    "Quelle est la vision du produit?",
    "Quelles sont les fonctionnalités principales?",
    "Qui sont les utilisateurs cibles?"
]

for q in queries:
    print(f"   Q: '{q}'")
    r = httpx.get(f"{API_URL}/api/search/test?q={q}", timeout=30)
    
    if r.status_code == 200:
        data = r.json()
        count = data['results_count']
        print(f"   → {count} résultats")
        
        if count > 0:
            best = data['results'][0]
            print(f"      Similarité: {best['similarity']:.3f}")
            print(f"      Preview: {best['content'][:80]}...")
    print()

print("✅ Tests terminés!")

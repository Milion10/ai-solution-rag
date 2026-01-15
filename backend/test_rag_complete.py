"""
Test complet du système RAG : Upload + Indexation + Recherche
"""
import sys
import os
import httpx
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
UPLOAD_DIR = Path("uploads")

print("=" * 70)
print("🧪 TEST COMPLET - SYSTÈME RAG")
print("=" * 70)

# Vérifier que le serveur est démarré
print("\n1️⃣ Vérification serveur...")
try:
    response = httpx.get(f"{API_BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Serveur démarré et opérationnel")
    else:
        print("   ❌ Serveur ne répond pas correctement")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Serveur non accessible: {e}")
    print("   💡 Assurez-vous que le serveur FastAPI est démarré")
    sys.exit(1)

# Chercher un PDF dans le dossier uploads
print("\n2️⃣ Recherche de PDF à tester...")
pdf_files = list(UPLOAD_DIR.glob("*.pdf"))

if not pdf_files:
    print("   ⚠️  Aucun PDF trouvé dans uploads/")
    print("   💡 Uploadez d'abord un PDF via Swagger: http://localhost:8000/docs")
    sys.exit(0)

pdf_path = pdf_files[0]
print(f"   ✅ PDF trouvé: {pdf_path.name} ({pdf_path.stat().st_size // 1024} KB)")

# Upload et indexation
print(f"\n3️⃣ Upload et indexation de {pdf_path.name}...")
try:
    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        params = {"auto_index": "true"}
        
        print("   ⏳ Upload en cours...")
        response = httpx.post(
            f"{API_BASE_URL}/api/documents/upload",
            files=files,
            params=params,
            timeout=300  # 5 minutes max
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Upload réussi!")
            print(f"      📄 Fichier: {data['filename']}")
            print(f"      📏 Taille: {data['size_bytes']} bytes")
            print(f"      📖 Pages: {data['page_count']}")
            print(f"      📝 Texte: {data['text_length']} caractères")
            
            if data.get('indexed'):
                print(f"      🧠 Indexé: OUI")
                print(f"      🆔 Document ID: {data['document_id']}")
                document_id = data['document_id']
            else:
                print(f"      ❌ Indexation: ÉCHEC")
                if 'indexing_error' in data:
                    print(f"      ⚠️  Erreur: {data['indexing_error']}")
                sys.exit(1)
        else:
            print(f"   ❌ Erreur upload: {response.status_code}")
            print(f"      {response.text}")
            sys.exit(1)

except Exception as e:
    print(f"   ❌ Erreur: {e}")
    sys.exit(1)

# Attendre un peu pour être sûr que tout est bien indexé
print("\n   ⏳ Attente 2 secondes pour stabilisation...")
time.sleep(2)

# Tests de recherche
print("\n4️⃣ Tests de recherche vectorielle...")

test_queries = [
    "Qu'est-ce que l'IA?",
    "Comment fonctionne le système?",
    "Quelles sont les fonctionnalités?",
    "Qui sont les utilisateurs?",
    "Quelle est l'architecture technique?"
]

print(f"\n   🔍 Test de {len(test_queries)} requêtes:\n")

for i, query in enumerate(test_queries, 1):
    try:
        response = httpx.get(
            f"{API_BASE_URL}/api/search/test",
            params={"q": query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results_count = data.get('results_count', 0)
            
            print(f"   {i}. 📝 '{query}'")
            print(f"      → {results_count} résultats trouvés")
            
            if results_count > 0:
                # Afficher le meilleur résultat
                best_result = data['results'][0]
                similarity = best_result['similarity']
                content_preview = best_result['content'][:100].replace('\n', ' ')
                
                print(f"      ✨ Meilleur match (similarité: {similarity:.3f}):")
                print(f"         '{content_preview}...'")
            else:
                print(f"      ⚠️  Aucun résultat (ajustez le seuil de similarité)")
            print()
        else:
            print(f"   ❌ Erreur requête {i}: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Erreur requête {i}: {e}")

# Test de recherche détaillée avec API POST
print("\n5️⃣ Test recherche détaillée (API POST)...")
try:
    search_request = {
        "query": "Quelle est la vision du produit?",
        "top_k": 3,
        "similarity_threshold": 0.3
    }
    
    response = httpx.post(
        f"{API_BASE_URL}/api/search/search",
        json=search_request,
        timeout=30
    )
    
    if response.status_code == 200:
        results = response.json()
        print(f"   ✅ {len(results)} résultats trouvés\n")
        
        for i, result in enumerate(results, 1):
            print(f"   Résultat {i}:")
            print(f"      📄 Fichier: {result['filename']}")
            print(f"      📊 Similarité: {result['similarity']:.3f}")
            print(f"      📝 Chunk #{result['chunk_index']}")
            content_preview = result['content'][:150].replace('\n', ' ')
            print(f"      💬 Contenu: '{content_preview}...'")
            print()
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"      {response.text}")

except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("=" * 70)
print("✅ TESTS TERMINÉS!")
print("=" * 70)
print("\n💡 Prochaine étape: Créer l'endpoint /chat avec LLM")
print("📊 Swagger UI: http://localhost:8000/docs")

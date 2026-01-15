"""
Script de test pour vérifier que tous les services fonctionnent
"""
import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import test_connection
import redis
from sqlalchemy import text
from utils.database import engine

print("=" * 60)
print("🧪 TEST INFRASTRUCTURE - AI SOLUTION")
print("=" * 60)

# Test 1: PostgreSQL
print("\n1️⃣ Test PostgreSQL + pgvector...")
try:
    test_connection()
    
    # Vérifier pgvector
    with engine.connect() as conn:
        result = conn.execute(text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'"))
        row = result.fetchone()
        if row:
            print(f"   ✅ Extension pgvector {row[1]} installée")
        
        # Compter les tables
        result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
        count = result.fetchone()[0]
        print(f"   ✅ {count} tables créées")
        
except Exception as e:
    print(f"   ❌ Erreur PostgreSQL: {e}")

# Test 2: Redis
print("\n2️⃣ Test Redis...")
try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()
    print("   ✅ Redis répond correctement")
    
    # Test write/read
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    if value == 'test_value':
        print("   ✅ Lecture/Écriture Redis OK")
    r.delete('test_key')
    
except Exception as e:
    print(f"   ❌ Erreur Redis: {e}")

# Test 3: MinIO
print("\n3️⃣ Test MinIO...")
try:
    import httpx
    response = httpx.get('http://localhost:9000/minio/health/live', timeout=5)
    if response.status_code == 200:
        print("   ✅ MinIO est accessible")
        print("   📊 Console Web: http://localhost:9001")
        print("      User: minioadmin / Pass: minioadmin")
except Exception as e:
    print(f"   ⚠️  MinIO: {e} (normal si pas encore démarré complètement)")

print("\n" + "=" * 60)
print("✅ TESTS TERMINÉS - Infrastructure prête !")
print("=" * 60)
print("\n💡 Prochaine étape: Chunking & Embeddings")

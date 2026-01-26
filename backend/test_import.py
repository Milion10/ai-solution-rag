"""
Test d'import pour diagnostiquer le problème
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("🧪 Test des imports...")

try:
    print("\n1️⃣ Import de llm_factory...")
    from ai.llm_factory import get_llm_generator
    print("✅ llm_factory importé")
    
    print("\n2️⃣ Création de l'instance LLM...")
    llm = get_llm_generator()
    print(f"✅ LLM créé: {llm.__class__.__name__}")
    
    print("\n3️⃣ Vérification de la santé...")
    health = llm.check_health()
    print(f"✅ Health check: {health}")
    
    print("\n4️⃣ Test de génération simple...")
    response = llm.generate("Dis bonjour", max_tokens=20)
    print(f"✅ Réponse: {response[:100]}...")
    
    print("\n✅ TOUS LES TESTS RÉUSSIS")
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

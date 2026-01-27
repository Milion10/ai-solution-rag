"""
Test rapide de l'endpoint chat pour diagnostiquer l'erreur 500
"""
import requests
import json

def test_chat_endpoint():
    """Teste l'endpoint /api/chat"""
    url = "http://localhost:8000/api/chat"
    
    payload = {
        "question": "Bonjour, comment vas-tu ?",
        "top_k": 5,
        "similarity_threshold": 0.3
    }
    
    print("🧪 Test de l'endpoint /api/chat")
    print(f"📤 Requête: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\n📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Succès!")
            data = response.json()
            print(f"📝 Réponse: {data.get('answer', '')[:200]}...")
        else:
            print(f"❌ Erreur {response.status_code}")
            try:
                error_data = response.json()
                print(f"Détails: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Texte brut: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_endpoint()

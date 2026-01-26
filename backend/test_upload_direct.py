"""
Test d'upload et indexation directe
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests

def test_upload():
    """Teste l'upload avec indexation"""
    
    print("\n" + "="*80)
    print("🧪 TEST UPLOAD + INDEXATION")
    print("="*80)
    
    # Vérifier qu'un fichier existe
    test_file = os.path.join(os.path.dirname(__file__), "uploads", "projet-ingenieur.pdf")
    if not os.path.exists(test_file):
        print(f"\n❌ Fichier de test introuvable: {test_file}")
        return
    
    print(f"\n📄 Upload du fichier: {test_file}")
    
    # Simuler un upload
    url = "http://localhost:8001/api/documents/upload"
    
    with open(test_file, 'rb') as f:
        files = {'file': (os.path.basename(test_file), f, 'application/pdf')}
        params = {
            'auto_index': 'true',
            'conversation_id': 'test_conv_manual_12345'
        }
        
        print(f"🚀 Envoi vers: {url}")
        print(f"   Params: {params}")
        
        response = requests.post(url, files=files, params=params)
        
        print(f"\n📥 Statut: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload réussi!")
            print(f"   Filename: {data.get('filename')}")
            print(f"   Indexed: {data.get('indexed')}")
            print(f"   Document ID: {data.get('document_id')}")
            
            if data.get('indexed'):
                print("\n🎉 Document indexé avec succès!")
            else:
                print(f"\n❌ Document NON indexé")
                if 'indexing_error' in data:
                    print(f"   Erreur: {data['indexing_error']}")
        else:
            print(f"❌ Erreur: {response.text}")

if __name__ == "__main__":
    test_upload()
    print("\n" + "="*80 + "\n")

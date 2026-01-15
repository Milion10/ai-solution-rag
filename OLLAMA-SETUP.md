# Installation et Configuration d'Ollama

## 📥 Installation

### Windows
1. Téléchargez Ollama : https://ollama.ai/download/windows
2. Exécutez l'installeur `OllamaSetup.exe`
3. Ollama démarre automatiquement en arrière-plan

### Vérification
```powershell
ollama --version
```

## 🤖 Téléchargement du Modèle Mistral 7B

```powershell
ollama pull mistral:7b-instruct
```

**Taille du téléchargement :** ~4.1 GB (modèle Q4 quantifié)

## ✅ Test du Modèle

```powershell
ollama run mistral:7b-instruct
```

Dans la console interactive :
```
>>> Bonjour, peux-tu te présenter ?
>>> /bye
```

## 🔌 API Ollama

Ollama expose une API REST sur `http://localhost:11434`

### Test de santé
```powershell
curl http://localhost:11434/api/tags
```

### Test de génération
```powershell
curl http://localhost:11434/api/generate -d '{
  "model": "mistral:7b-instruct",
  "prompt": "Dis bonjour en français",
  "stream": false
}'
```

## 🎯 Modèles Alternatifs

Si Mistral est trop lourd pour votre machine :

```powershell
# Phi-3 Mini (3.8B paramètres, ~2.3 GB)
ollama pull phi3:mini

# Llama 3.2 (3B paramètres, ~2 GB)
ollama pull llama3.2:3b
```

Puis modifiez dans `ai/llm.py` :
```python
model: str = "phi3:mini"  # ou "llama3.2:3b"
```

## 📊 Utilisation Mémoire

- **Mistral 7B Q4** : ~4-5 GB RAM
- **Phi-3 Mini** : ~2-3 GB RAM
- **Llama 3.2 3B** : ~2-3 GB RAM

## 🔧 Configuration Avancée

### Modifier le port Ollama (optionnel)
```powershell
# Variables d'environnement
$env:OLLAMA_HOST = "0.0.0.0:11434"
```

### Performance GPU (si disponible)
Ollama détecte automatiquement votre GPU (NVIDIA/AMD) et l'utilise.

## 🚀 Démarrage Automatique

Ollama démarre automatiquement avec Windows. Pour le gérer :

```powershell
# Arrêter Ollama
taskkill /IM ollama.exe /F

# Redémarrer (via icône système ou exécutez)
ollama serve
```

## 📚 Documentation

- Site officiel : https://ollama.ai
- GitHub : https://github.com/ollama/ollama
- Modèles disponibles : https://ollama.ai/library

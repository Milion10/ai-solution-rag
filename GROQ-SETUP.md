# 🚀 Configuration Groq - Guide Rapide

## ✅ Configuration Terminée

Tu es maintenant configuré avec **Groq** pour un développement ultra-rapide !

### 🎯 Avantages
- ⚡ **Réponses en <2 secondes** (au lieu de 40 secondes)
- 🆓 **Gratuit** pour le développement
- 🔄 **Facile à basculer** vers Ollama pour la production

---

## 📊 Comparaison Avant/Après

| Critère | Avant (Ollama) | Après (Groq) |
|---------|----------------|--------------|
| **Temps de réponse** | 40 secondes ⏱️ | 1-2 secondes ⚡ |
| **Modèle** | Mistral 7B local | Llama 3.3 70B cloud |
| **Coût** | Gratuit | Gratuit (limites) |
| **Privacy** | 100% local 🔒 | Cloud ☁️ |

---

## 🔧 Configuration Actuelle

### Fichier `.env` (Backend)
```env
LLM_PROVIDER=groq
GROQ_API_KEY=votre_clé_api_groq_ici
GROQ_MODEL=llama-3.3-70b-versatile
```

### Modèles Groq Disponibles
- `llama-3.3-70b-versatile` (actuel) - Excellent pour tout usage
- `llama-3.1-70b-versatile` - Alternative stable
- `llama3-8b-8192` - Plus léger, encore plus rapide
- `gemma2-9b-it` - Bon compromis vitesse/qualité

---

## 🔄 Basculer entre Groq et Ollama

### Pour le développement (Groq - rapide)
Dans `backend/.env` :
```env
LLM_PROVIDER=groq
```

### Pour la production (Ollama - local/privé)
Dans `backend/.env` :
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct
```

Puis redémarrer le backend :
```bash
cd ai-solution
.\stop-app.ps1
.\start-app.ps1
```

---

## 🧪 Tester la Configuration

### Test rapide
```bash
cd ai-solution/backend
..\..\.venv\Scripts\python.exe test_groq.py
```

### Test dans l'application
1. Ouvre http://localhost:3000/chat
2. Pose une question
3. La réponse devrait arriver en **1-2 secondes** ⚡

---

## 📦 Fichiers Modifiés

### Nouveaux fichiers
- ✅ `backend/ai/llm_factory.py` - Factory pour gérer les providers
- ✅ `backend/test_groq.py` - Script de test
- ✅ `backend/.env.example` - Template de configuration

### Fichiers modifiés
- ✅ `backend/.env` - Configuration Groq
- ✅ `backend/requirements.txt` - Ajout du package groq
- ✅ `backend/api/chat.py` - Import du nouveau factory

---

## 🔐 Sécurité

⚠️ **Important** : Ta clé API Groq est dans `.env` (ignoré par Git).

### Renouveler la clé API (si besoin)
1. Va sur https://console.groq.com/keys
2. Révoque l'ancienne clé
3. Crée une nouvelle clé
4. Remplace dans `backend/.env`

---

## 📈 Limites Groq (Plan Gratuit)

- **Requêtes/minute** : ~30 requêtes
- **Tokens/minute** : ~6000 tokens
- **Tokens/jour** : Illimité

Pour le développement, c'est **largement suffisant** ! 🎉

---

## 🆘 Troubleshooting

### Erreur "Model decommissioned"
Le modèle n'est plus disponible. Change dans `.env` :
```env
GROQ_MODEL=llama-3.3-70b-versatile
```

### Erreur "API Key invalid"
Vérifie que ta clé est bien copiée dans `.env`

### Réponses lentes
Tu utilises peut-être encore Ollama. Vérifie :
```env
LLM_PROVIDER=groq  # Doit être "groq" et pas "ollama"
```

---

## 🎓 Prochaines Étapes

1. ✅ **Teste l'application** - Les réponses devraient être ultra-rapides
2. 📝 **Développe tranquillement** - Plus besoin d'attendre 40 secondes !
3. 🚀 **En production** - Bascule vers Ollama pour privacy totale

---

## 💡 Astuce Pro

Pour basculer rapidement entre providers, crée des alias :
```powershell
# Dans ton profil PowerShell
function Use-Groq { (Get-Content backend\.env) -replace 'LLM_PROVIDER=ollama', 'LLM_PROVIDER=groq' | Set-Content backend\.env }
function Use-Ollama { (Get-Content backend\.env) -replace 'LLM_PROVIDER=groq', 'LLM_PROVIDER=ollama' | Set-Content backend\.env }
```

Ensuite :
```powershell
Use-Groq    # Passe à Groq (dev rapide)
Use-Ollama  # Passe à Ollama (prod locale)
```

---

**Tu es prêt ! Enjoy la vitesse de développement ! 🚀**

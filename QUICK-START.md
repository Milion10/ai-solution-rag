# 🚀 Démarrage Rapide - AI Solution

## Lancement de l'application complète

### Option 1 : Script automatique (RECOMMANDÉ) ⭐

Ouvrez PowerShell et exécutez :

```powershell
cd C:\Users\axelm\OneDrive\Documents\Code\Projet-ia\ai-solution
.\start-app.ps1
```

Le script va :
1. ✅ Vérifier Docker
2. ✅ Démarrer PostgreSQL, Redis, MinIO
3. ✅ Lancer le backend FastAPI (nouveau terminal)
4. ✅ Lancer le frontend Next.js (nouveau terminal)
5. ✅ Ouvrir votre navigateur sur http://localhost:3000

**Pour arrêter** :
```powershell
.\stop-app.ps1
```

---

## 🔧 Prérequis (à faire une seule fois)

### 1. Installer Docker Desktop
- Télécharger : https://www.docker.com/products/docker-desktop/
- **Important** : Docker doit être démarré avant de lancer l'application

### 2. Vérifier l'environnement virtuel Python
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Installer les dépendances Node.js
```powershell
cd frontend
npm install
```

---

## ❓ FAQ - Pourquoi c'était compliqué avant ?

**Problème 1 : Docker non lancé**
- L'application a besoin de PostgreSQL (base de données)
- PostgreSQL tourne dans Docker
- **Solution** : Le script vérifie et lance Docker automatiquement

**Problème 2 : Le backend ne trouvait pas ses modules**
- Python ne savait pas où chercher les fichiers
- **Solution** : Le script configure automatiquement `PYTHONPATH`

**Problème 3 : Plusieurs terminaux à gérer**
- Backend et Frontend doivent tourner en parallèle
- **Solution** : Le script ouvre automatiquement 2 nouveaux terminaux

**Problème 4 : Ordre de démarrage**
- PostgreSQL doit être prêt avant le backend
- **Solution** : Le script attend 5 secondes après Docker

---

## 📍 URLs importantes

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interface utilisateur |
| **Backend** | http://localhost:8000 | API REST |
| **API Docs** | http://localhost:8000/docs | Documentation Swagger |
| **MinIO** | http://localhost:9001 | Stockage fichiers (minioadmin/minioadmin) |
| **PostgreSQL** | localhost:5432 | Base de données |
| **Redis** | localhost:6379 | Cache |

---

## 🐛 Dépannage

### "Docker n'est pas installé ou pas démarré"
1. Ouvrez Docker Desktop
2. Attendez qu'il soit complètement démarré (icône verte)
3. Relancez `.\start-app.ps1`

### "Environnement virtuel non trouvé"
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "node_modules non trouvé"
```powershell
cd frontend
npm install
```

### Le backend ou frontend ne démarre pas
- Fermez tous les terminaux PowerShell
- Relancez `.\start-app.ps1`

### Ports déjà utilisés
Si un service ne démarre pas (port occupé), trouvez le processus :
```powershell
# Port 3000 (frontend)
netstat -ano | findstr :3000
# Port 8000 (backend)
netstat -ano | findstr :8000
# Port 5432 (PostgreSQL)
netstat -ano | findstr :5432
```

Puis tuez le processus :
```powershell
taskkill /PID <numéro_PID> /F
```

---

## 🎯 Avantages du nouveau système

| Avant | Maintenant |
|-------|------------|
| ❌ 5 commandes à exécuter | ✅ 1 seule commande |
| ❌ 3 terminaux à gérer | ✅ Script automatique |
| ❌ Attendre manuellement | ✅ Attentes gérées |
| ❌ Oublier Docker | ✅ Vérification auto |
| ❌ Erreurs PYTHONPATH | ✅ Configuration auto |
| ⏱️ ~5 minutes | ⚡ ~15 secondes |

---

## 📝 Notes

- Les modifications de code sont détectées automatiquement (hot reload)
- Les terminaux doivent rester ouverts pendant que vous travaillez
- Fermez proprement avec `stop-app.ps1` pour éviter les processus orphelins

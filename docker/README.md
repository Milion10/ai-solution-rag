# Docker - Configuration Déploiement

Configuration Docker Compose pour déploiement complet de la solution.

## 🚀 Démarrage Rapide

**1. Prérequis:**
- Docker Desktop 24+ installé et démarré
- 16GB RAM disponible minimum

**2. Lancer tous les services:**
```bash
cd docker
docker-compose up -d
```

**3. Vérifier statut:**
```bash
docker-compose ps
```

**4. Voir logs:**
```bash
docker-compose logs -f
```

**5. Arrêter services:**
```bash
docker-compose down
```

**6. Supprimer volumes (ATTENTION: perte données):**
```bash
docker-compose down -v
```

## 📦 Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | Interface Next.js |
| backend | 8000 | API FastAPI |
| postgres | 5432 | Base données + pgvector |
| redis | 6379 | Cache |
| minio | 9000, 9001 | Stockage fichiers (console: 9001) |

## 🔐 Accès Interfaces

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (user: minioadmin, pass: minioadmin)

## 📁 Volumes

Données persistées dans `docker/volumes/`:
- `postgres-data/`: Base données PostgreSQL
- `minio-data/`: Fichiers MinIO
- `redis-data/`: Cache Redis

**⚠️ Ne pas committer `volumes/` (dans .gitignore)**

## 🛠️ Configuration

Variables d'environnement dans `docker/.env`:
```env
# Database
POSTGRES_USER=ai_user
POSTGRES_PASSWORD=change-me-in-production
POSTGRES_DB=ai_solution

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Backend
JWT_SECRET=your-secret-key-change-in-production
```

## 🧪 Mode Développement

Pour développer sans Docker:
1. Lancer uniquement infra: `docker-compose up postgres redis minio -d`
2. Backend local: `cd ../backend && uvicorn main:app --reload`
3. Frontend local: `cd ../frontend && npm run dev`

## 📝 Notes

- Modèle LLM (GGUF) à monter en volume dans backend
- pgvector installé via image docker spéciale PostgreSQL
- Réseau Docker `ai-network` pour communication inter-services

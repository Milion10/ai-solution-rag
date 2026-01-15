# Backend - FastAPI + RAG

API REST pour la solution IA conversationnelle.

## 🚀 Installation Locale (Développement)

**1. Créer environnement virtuel:**
```bash
cd backend
python -m venv venv
```

**2. Activer environnement:**
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

**3. Installer dépendances:**
```bash
pip install -r requirements.txt
```

**4. Variables d'environnement:**
Créer `.env` dans `backend/`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_solution
REDIS_URL=redis://localhost:6379
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
JWT_SECRET=your-secret-key-here-change-in-production
```

**5. Démarrer serveur:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API disponible sur http://localhost:8000  
Documentation auto: http://localhost:8000/docs

## 📁 Structure

```
backend/
├── main.py              # Point d'entrée FastAPI
├── requirements.txt     # Dépendances Python
├── Dockerfile           # Image Docker
├── api/                 # Routes API
│   ├── __init__.py
│   ├── chat.py          # Endpoints chat
│   ├── documents.py     # Upload/gestion docs
│   └── auth.py          # Authentification
├── ai/                  # RAG Pipeline
│   ├── __init__.py
│   ├── embeddings.py    # Génération embeddings
│   ├── llm.py           # LLM local (Mistral/Llama)
│   ├── rag_pipeline.py  # Orchestration RAG
│   └── chunking.py      # Découpage documents
├── models/              # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── conversation.py
│   ├── message.py
│   └── document.py
├── services/            # Business logic
│   ├── __init__.py
│   ├── auth_service.py
│   ├── chat_service.py
│   └── document_service.py
└── utils/               # Utilitaires
    ├── __init__.py
    ├── database.py      # Connexion DB
    ├── minio_client.py  # Client MinIO
    └── redis_client.py  # Client Redis
```

## 🧪 Tests

```bash
pytest tests/
```

## 📝 Notes

- LLM modèles (GGUF) à télécharger dans `models/` (non versionnés)
- MinIO utilisé pour stockage fichiers (S3-compatible)
- pgvector pour embeddings vectoriels

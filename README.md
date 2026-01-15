# AI Solution - IA Conversationnelle On-Premise

Solution IA conversationnelle privée pour PME tech avec RAG (Retrieval-Augmented Generation).

## 🚀 Quick Start

**Pré-requis:**
- Docker Desktop 24+ installé
- 16GB RAM minimum
- Python 3.11+ (pour développement backend)
- Node.js 20+ (pour développement frontend)

**Démarrage rapide:**
```bash
cd docker
docker-compose up -d
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Structure Projet

```
ai-solution/
├── frontend/           # Next.js App Router
├── backend/            # FastAPI + RAG
├── docker/             # Docker Compose + Dockerfiles
├── docs/               # Documentation
└── scripts/            # Scripts utilitaires
```

## 🎓 Phase Actuelle: POC (Proof of Concept)

Objectif: Valider stack technique avec chat fonctionnel + RAG sur 1 PDF.

**Fonctionnalités POC:**
- ✅ Chat conversationnel basique
- ✅ Upload 1 PDF
- ✅ RAG pipeline (chunking, embeddings, recherche)
- ✅ LLM local (Mistral 7B ou Llama 3.1 8B GGUF Q4)
- ✅ Interface type ChatGPT

**Hors scope POC:**
- Auth JWT (Phase 1)
- Multi-documents (Phase 1)
- Profils utilisateurs (Phase 1)
- Citations avancées (Phase 1)

## 📚 Documentation

Voir `docs/` pour guides détaillés:
- Installation complète
- Architecture technique
- Guides développement
- API Reference

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 + Tailwind + shadcn/ui
- **Backend**: FastAPI + Python 3.11
- **IA**: LangChain + Mistral/Llama (GGUF) + sentence-transformers
- **Base données**: PostgreSQL 16 + pgvector
- **Stockage**: MinIO (S3-compatible)
- **Cache**: Redis

## 📝 License

Propriétaire - Tous droits réservés

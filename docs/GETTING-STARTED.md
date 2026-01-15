# Guide de Démarrage - Développeur Débutant

Ce guide vous accompagne **étape par étape** pour comprendre et développer le projet.

## 🎓 Prérequis Apprentissage

**Avant de coder, comprendre les bases:**

### 1. Python & FastAPI (1-2 semaines)
- ✅ **Tutorial FastAPI officiel**: https://fastapi.tiangolo.com/tutorial/
  - Endpoints GET/POST
  - Path parameters, Query parameters
  - Request body (Pydantic)
  - Dépendances (dependency injection)
- ✅ **Async/await en Python**: Comprendre `async def`, `await`

### 2. Next.js & React (1-2 semaines)
- ✅ **Next.js Learn**: https://nextjs.org/learn
  - App Router (nouveau système)
  - Server Components vs Client Components
  - Routing, layouts
- ✅ **React Hooks**: useState, useEffect, useRef
- ✅ **TypeScript basics**: Types, interfaces, génériques

### 3. LangChain & RAG (1 semaine)
- ✅ **LangChain Tutorials**: https://python.langchain.com/docs/tutorials/
  - RAG quickstart
  - Document loaders
  - Vector stores
  - LLM chains
- ✅ **Comprendre RAG**: Retrieval-Augmented Generation (chercher vidéos YouTube)

### 4. Docker (3-4 jours)
- ✅ **Docker Getting Started**: https://docs.docker.com/get-started/
  - Dockerfile
  - docker-compose
  - Volumes, networks
- ✅ **Pratiquer**: Lancer PostgreSQL, Redis en conteneurs

## 🏗️ Phase 0: POC (3-4 semaines)

### Objectif
Créer un chat fonctionnel qui répond intelligemment à partir d'1 PDF.

### Architecture POC
```
[Frontend Next.js] → [Backend FastAPI] → [LLM Local]
                            ↓
                      [PostgreSQL + pgvector]
                            ↓
                      [Embeddings du PDF]
```

### Étapes de Développement

#### ✅ Étape 1: Backend Minimal (Semaine 1)
**Fichiers à créer:**
- `backend/main.py`: Endpoints `/health`, `/chat` (POST)
- `backend/requirements.txt`: Dépendances

**À apprendre:**
- Créer endpoint FastAPI
- Tester avec Swagger UI (/docs)
- Retourner JSON simple

**Test:**
```bash
curl http://localhost:8000/health
# Doit retourner: {"status": "healthy"}
```

#### ✅ Étape 2: Upload & Parsing PDF (Semaine 1-2)
**Fichiers à créer:**
- `backend/api/documents.py`: Endpoint `/upload` (POST)
- `backend/ai/document_parser.py`: Extraction texte PDF

**À apprendre:**
- Multipart form data (upload fichier)
- Librairie `pypdf` pour parser PDF
- Sauvegarder fichier temporairement

**Test:**
```bash
# Upload PDF via Swagger UI
# Voir texte extrait dans logs
```

#### ✅ Étape 3: Embeddings & pgvector (Semaine 2)
**Fichiers à créer:**
- `backend/ai/embeddings.py`: Génération embeddings
- `backend/ai/chunking.py`: Découpage texte en chunks
- `backend/utils/database.py`: Connexion PostgreSQL + pgvector

**À apprendre:**
- sentence-transformers (all-MiniLM-L6-v2)
- Découpage texte (512 tokens par chunk)
- Créer table PostgreSQL avec colonne `vector`

**Test:**
```python
# Générer embeddings pour "Bonjour le monde"
# Sauvegarder dans pgvector
# Requête similarité cosine
```

#### ✅ Étape 4: RAG Pipeline (Semaine 2-3)
**Fichiers à créer:**
- `backend/ai/rag_pipeline.py`: Orchestration RAG
- `backend/ai/llm.py`: LLM local (Mistral/Llama)

**À apprendre:**
- LangChain RetrievalQA
- Charger modèle GGUF avec llama-cpp-python
- Construire prompt avec contexte

**Workflow:**
1. User: "Quel est le sujet du document?"
2. Backend: Génère embedding de la question
3. pgvector: Recherche top 3 chunks similaires
4. LLM: Génère réponse avec contexte chunks
5. Return: Réponse + citations

**Test:**
```python
# Question: "De quoi parle ce document?"
# Réponse attendue: Résumé intelligent basé sur PDF
```

#### ✅ Étape 5: Frontend Chat (Semaine 3)
**Fichiers à créer:**
- `frontend/app/chat/page.tsx`: Page chat
- `frontend/components/chat/ChatMessage.tsx`: Composant message
- `frontend/components/chat/ChatInput.tsx`: Input utilisateur
- `frontend/lib/api.ts`: Client API

**À apprendre:**
- useState pour gérer messages
- Fetch API vers backend
- Affichage messages (user vs AI)
- Auto-scroll vers bas

**Test:**
- Taper question
- Voir réponse IA s'afficher
- Historique conversationnel

#### ✅ Étape 6: Docker Compose (Semaine 4)
**Fichiers à créer:**
- `docker/docker-compose.yml`: Orchestration services
- `docker/backend.Dockerfile`: Image backend
- `docker/frontend.Dockerfile`: Image frontend

**À apprendre:**
- Multi-stage builds
- Volumes persistants
- Networks Docker
- Variables d'environnement

**Test:**
```bash
docker-compose up -d
# Vérifier tous services démarrent
# Tester chat end-to-end
```

## 🐛 Debugging Tips

**Backend (FastAPI):**
- Logs dans terminal: `print()` ou `logger.info()`
- Swagger UI: http://localhost:8000/docs (tester endpoints)
- Erreurs Python: Lire stacktrace complet

**Frontend (Next.js):**
- Console navigateur: `console.log()`
- Erreurs réseau: Onglet Network DevTools
- React DevTools: Inspecter state/props

**Docker:**
- Logs service: `docker-compose logs backend`
- Entrer dans conteneur: `docker exec -it backend bash`
- Vérifier volumes: `docker volume ls`

## 📚 Ressources Essentielles

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/docs
- LangChain: https://python.langchain.com/docs
- pgvector: https://github.com/pgvector/pgvector

**Vidéos Recommandées:**
- "FastAPI Crash Course" - freeCodeCamp
- "Next.js 14 Tutorial" - Traversy Media
- "RAG Explained" - AI Explained
- "LangChain Quickstart" - Sam Witteveen

**Communautés:**
- Discord FastAPI / LangChain
- Reddit: r/FastAPI, r/nextjs, r/LocalLLaMA
- Stack Overflow

## 💡 Conseils Apprentissage

1. **Ne pas tout apprendre avant de commencer**: Apprendre en faisant
2. **Copier-coller intelligemment**: Comprendre code avant de copier
3. **Debugging > Google**: Apprendre à debugger économise temps
4. **Petits commits Git**: Commit régulier = retour arrière facile
5. **Poser questions**: StackOverflow, Discord, ChatGPT

## 🎯 Prochaine Étape

➡️ **Commencer par Backend Minimal (Étape 1)**

Créer `backend/main.py` avec endpoint `/health` et le tester.

Prêt ? On y va ! 🚀

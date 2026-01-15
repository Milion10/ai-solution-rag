-- Init script pour PostgreSQL avec pgvector
-- S'exécute automatiquement au premier démarrage

-- Créer extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Vérifier installation
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Table pour stocker les documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    scope VARCHAR(20) NOT NULL DEFAULT 'admin',
    user_id UUID NULL,
    conversation_id UUID NULL,
    uploaded_by UUID NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    indexed_at TIMESTAMP NULL,
    last_used_at TIMESTAMP NULL,
    last_accessed_at TIMESTAMP NULL,
    access_count INTEGER DEFAULT 0,
    is_indexed BOOLEAN DEFAULT FALSE,
    indexing_status VARCHAR(20) DEFAULT 'pending',
    indexing_error TEXT NULL,
    metadata JSONB NULL
);

-- Table pour stocker les chunks avec embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),  -- all-MiniLM-L6-v2 = 384 dimensions (plus léger que 768)
    metadata JSONB NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);

-- Index pour recherche vectorielle (HNSW = meilleure performance)
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
ON document_chunks 
USING hnsw (embedding vector_cosine_ops);

-- Index classiques pour performances
CREATE INDEX IF NOT EXISTS documents_uploaded_at_idx ON documents(uploaded_at);
CREATE INDEX IF NOT EXISTS documents_scope_idx ON documents(scope);
CREATE INDEX IF NOT EXISTS document_chunks_document_id_idx ON document_chunks(document_id);

-- Table utilisateurs (pour plus tard)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL
);

-- Table profils utilisateurs (pour personnalisation)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(100) NULL,  -- Rôle professionnel (dev, hr, pm, etc.)
    seniority VARCHAR(50) NULL,
    interests TEXT[] NULL,
    preferences JSONB NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP NULL,
    is_archived BOOLEAN DEFAULT FALSE
);

-- Table messages
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender VARCHAR(10) NOT NULL,  -- 'user' ou 'ai'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB NULL
);

-- Table citations (sources des réponses IA)
CREATE TABLE IF NOT EXISTS citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(20) NOT NULL,
    excerpt_text TEXT NOT NULL,
    page_number INTEGER NULL,
    chunk_index INTEGER NOT NULL,
    similarity_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Afficher confirmation
SELECT 'Database initialized successfully!' AS status;

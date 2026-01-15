-- Tables pour le backend Python (documents + chunks vectoriels)
-- À exécuter dans la même base que les tables Prisma

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Table documents (backend Python)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    scope VARCHAR(50) NOT NULL DEFAULT 'admin',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_indexed BOOLEAN DEFAULT false,
    indexing_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table document_chunks (backend Python avec embeddings)
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);

-- Index pour recherche vectorielle
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id 
ON document_chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_documents_scope 
ON documents(scope);

CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at 
ON documents(uploaded_at);

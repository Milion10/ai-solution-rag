-- Migration: Ajout support organisations dans table documents
-- Date: 2026-01-13
-- Description: Ajoute user_id et organization_id pour gérer documents personnels vs partagés

-- Ajouter colonne user_id (nullable pour documents d'organisation)
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS user_id TEXT;

-- Ajouter colonne organization_id (nullable pour documents personnels)
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS organization_id TEXT;

-- Index pour performance sur les requêtes filtrées
CREATE INDEX IF NOT EXISTS idx_documents_organization_id ON documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_org_user ON documents(organization_id, user_id);

-- Commentaires pour documentation
COMMENT ON COLUMN documents.user_id IS 'ID de l''utilisateur propriétaire. NULL si document d''organisation.';
COMMENT ON COLUMN documents.organization_id IS 'ID de l''organisation propriétaire du document. NULL si document personnel.';

-- Migration des données existantes: documents sans owner restent accessibles à tous
-- Les nouveaux documents devront avoir soit user_id soit organization_id renseigné

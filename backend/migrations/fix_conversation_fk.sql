-- Migration: Supprimer contrainte FK sur conversation_id
-- Date: 2026-01-26
-- Raison: Les documents peuvent être uploadés AVANT la création de la conversation
-- Solution: Rendre conversation_id nullable sans FK

-- 1. Supprimer la contrainte de clé étrangère si elle existe
ALTER TABLE documents 
DROP CONSTRAINT IF EXISTS documents_conversation_id_fkey;

-- 2. S'assurer que la colonne conversation_id existe et est nullable
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS conversation_id TEXT;

-- 3. Ajouter un index pour les performances
CREATE INDEX IF NOT EXISTS idx_documents_conversation_id ON documents(conversation_id);

-- Commentaire
COMMENT ON COLUMN documents.conversation_id IS 'ID de la conversation à laquelle appartient le document. Null si document global/utilisateur.';

-- Note: Pas de contrainte FK car les documents peuvent être uploadés avant la création
-- de la conversation (upload pendant la saisie du premier message)

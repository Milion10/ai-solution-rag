"""
Service de stockage des documents et embeddings dans PostgreSQL + pgvector
"""
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from utils.database import engine, SessionLocal
from ai.chunking import get_chunker
from ai.embeddings import get_embeddings_generator
from typing import List, Dict
import uuid
import logging
import json

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Gère le stockage et la recherche de vecteurs dans pgvector
    """
    
    def __init__(self):
        self.chunker = get_chunker()
        self.embeddings = get_embeddings_generator()
        self.embedding_dim = self.embeddings.embedding_dim
    
    
    def store_document(
        self,
        filename: str,
        content: str,
        file_path: str,
        file_type: str,
        file_size: int,
        page_count: int = None,
        scope: str = "admin",
        user_id: str = None,
        organization_id: str = None,
        conversation_id: str = None
    ) -> str:
        """
        Stocke un document et génère ses chunks + embeddings
        
        Args:
            filename: Nom du fichier
            content: Contenu textuel extrait
            file_path: Chemin du fichier
            file_type: Type de fichier (pdf, docx, etc.)
            file_size: Taille en bytes
            page_count: Nombre de pages
            scope: Portée du document (organization, user)
            user_id: ID de l'utilisateur propriétaire (pour docs personnels)
            organization_id: ID de l'organisation (pour docs partagés)
        
        Returns:
            document_id (UUID string)
        """
        document_id = str(uuid.uuid4())
        
        logger.info(f"📝 Stockage document: {filename} (id: {document_id[:8]}...)")
        
        try:
            with SessionLocal() as db:
                # 1. Insérer le document

                insert_doc_query = text("""
                    INSERT INTO documents (
                        id, filename, file_type, file_size, file_path, 
                        scope, user_id, organization_id, conversation_id, uploaded_at, is_indexed, indexing_status
                    )
                    VALUES (
                        :id, :filename, :file_type, :file_size, :file_path,
                        :scope, :user_id, :organization_id, :conversation_id, CURRENT_TIMESTAMP, false, 'processing'
                    )
                """)
                db.execute(insert_doc_query, {
                    "id": document_id,
                    "filename": filename,
                    "file_type": file_type,
                    "file_size": file_size,
                    "file_path": file_path,
                    "scope": scope,
                    "user_id": user_id,
                    "organization_id": organization_id,
                    "conversation_id": conversation_id
                })
                db.commit()
                logger.info(f"  ✅ Document enregistré en DB (conversation_id={conversation_id})")
                
                # 2. Découper en chunks
                chunks = self.chunker.chunk_document(
                    text=content,
                    document_id=document_id,
                    filename=filename,
                    page_count=page_count
                )
                
                if not chunks:
                    logger.error("Aucun chunk généré!")
                    raise ValueError("Le document ne contient pas de texte exploitable")
                
                logger.info(f"  ✂️  {len(chunks)} chunks générés")
                
                # 3. Générer embeddings en batch (plus rapide)
                texts = [chunk["content"] for chunk in chunks]
                embeddings = self.embeddings.generate_embeddings(texts)
                
                logger.info(f"  🧠 {len(embeddings)} embeddings générés")
                
                # 4. Insérer chunks + embeddings
                insert_chunk_query = text("""
                    INSERT INTO document_chunks (
                        id, document_id, chunk_index, content, embedding, metadata
                    )
                    VALUES (
                        :id, :document_id, :chunk_index, :content, :embedding, :metadata
                    )
                """)
                
                for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    chunk_id = str(uuid.uuid4())
                    
                    # Nettoyer le contenu (supprimer caractères NULL)
                    clean_content = chunk["content"].replace('\x00', '')
                    
                    # Convertir embedding numpy en liste pour PostgreSQL
                    embedding_list = embedding.tolist()
                    
                    # Convertir metadata en JSON string
                    metadata_json = json.dumps(chunk.get("metadata", {}))
                    
                    db.execute(insert_chunk_query, {
                        "id": chunk_id,
                        "document_id": document_id,
                        "chunk_index": idx,
                        "content": clean_content,
                        "embedding": f"[{','.join(map(str, embedding_list))}]",
                        "metadata": metadata_json
                    })
                
                db.commit()
                
                logger.info(f"  💾 {len(chunks)} chunks stockés dans pgvector")
                
                # 5. Mettre à jour statut document
                update_doc_query = text("""
                    UPDATE documents
                    SET is_indexed = true, 
                        indexing_status = 'completed',
                        indexed_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """)
                
                db.execute(update_doc_query, {"id": document_id})
                db.commit()
                
                logger.info(f"✅ Document {filename} indexé avec succès!")
                
                return document_id
        
        except Exception as e:
            logger.error(f"❌ Erreur stockage document: {e}")
            import traceback
            logger.error(f"Traceback complet:\n{traceback.format_exc()}")
            
            # Marquer comme erreur dans DB
            try:
                with SessionLocal() as db:
                    update_error_query = text("""
                        UPDATE documents
                        SET indexing_status = 'failed',
                            indexing_error = :error
                        WHERE id = :id
                    """)
                    db.execute(update_error_query, {
                        "id": document_id,
                        "error": str(e)
                    })
                    db.commit()
            except:
                pass
            
            raise
    
    
    def search_similar(
        self,
        query_text: str,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
        user_id: str = None,
        organization_id: str = None,
        conversation_id: str = None
    ) -> List[Dict]:
        """
        Recherche les chunks les plus similaires à une requête
        
        Args:
            query_text: Texte de la requête
            top_k: Nombre de résultats à retourner
            similarity_threshold: Seuil de similarité minimum (0-1)
            user_id: ID de l'utilisateur pour filtrer ses documents (optionnel)
            organization_id: ID de l'organisation pour filtrer documents partagés (optionnel)
        
        Returns:
            Liste de dictionnaires avec chunks et scores de similarité
        """
        logger.info(f"🔍 Recherche similaire: '{query_text[:50]}...' (user: {user_id or 'all'}, org: {organization_id or 'none'})")
        
        # Générer embedding de la requête
        query_embedding = self.embeddings.generate_embedding(query_text)
        query_embedding_list = query_embedding.tolist()
        query_vector_str = f"[{','.join(map(str, query_embedding_list))}]"
        
        with SessionLocal() as db:
            # Recherche par similarité cosine avec pgvector
            # Stratégie :
            # - Toujours inclure les documents globaux de l'organisation
            # - Toujours inclure les documents personnels de l'utilisateur
            # - Si conversation_id fourni, AJOUTER les documents de cette conversation
            # Résultat : cherche dans (globaux + perso + conversation) simultanément
            
            where_conditions = []
            
            # Documents d'organisation (globaux) - toujours inclus si org_id fourni
            if organization_id:
                where_conditions.append("(d.scope = 'organization' AND d.organization_id = :org_id)")
            
            # Documents personnels de l'utilisateur - toujours inclus si user_id fourni
            if user_id:
                where_conditions.append("(d.scope = 'user' AND d.user_id = :user_id)")
            
            # Documents de conversation - AJOUTÉS en plus si conversation_id fourni
            if conversation_id:
                where_conditions.append("(d.conversation_id = :conversation_id)")
            
            # Si aucun filtre, chercher dans tous les documents (fallback)
            if not where_conditions:
                where_conditions.append("1=1")
            
            where_clause = " OR ".join(where_conditions)
            
            logger.info(f"  📊 Recherche dans: organization={bool(organization_id)}, user={bool(user_id)}, conversation={bool(conversation_id)}")
            logger.info(f"  🔍 WHERE clause: {where_clause}")
            logger.info(f"  🎯 Params: org_id={organization_id}, user_id={user_id}, conv_id={conversation_id}")
            
            search_query = text(f"""
                SELECT 
                    dc.id,
                    dc.document_id,
                    dc.chunk_index,
                    dc.content,
                    d.filename,
                    d.file_type,
                    d.scope,
                    1 - (dc.embedding <=> CAST(:query_embedding AS vector)) as similarity
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE 1 - (dc.embedding <=> CAST(:query_embedding AS vector)) >= :threshold
                AND ({where_clause})
                ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
                LIMIT :top_k
            """)
            result = db.execute(search_query, {
                "query_embedding": query_vector_str,
                "threshold": similarity_threshold,
                "top_k": top_k,
                "org_id": organization_id,
                "user_id": user_id,
                "conversation_id": conversation_id
            })
            
            results = []
            for row in result:
                results.append({
                    "chunk_id": row[0],
                    "document_id": row[1],
                    "chunk_index": row[2],
                    "content": row[3],
                    "filename": row[4],
                    "file_type": row[5],
                    "scope": row[6],
                    "similarity": float(row[7])
                })
            
            logger.info(f"  ✅ {len(results)} résultats trouvés")
            
            return results


# Instance globale
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    """Retourne l'instance singleton du vector store"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance


if __name__ == "__main__":
    # Test du vector store
    import sys
    sys.path.insert(0, "..")
    
    store = VectorStore()
    print(f"\n✅ VectorStore initialisé")
    print(f"📐 Embedding dimensions: {store.embedding_dim}")
    print(f"\n💡 Utilisez l'endpoint /upload pour tester le stockage complet")

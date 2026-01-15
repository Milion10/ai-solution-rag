"""
API Routes pour gestion des documents
Upload, parsing PDF, gestion fichiers
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import pypdf
import pdfplumber
import os
import logging
from pathlib import Path
from ai.vector_store import get_vector_store

logger = logging.getLogger(__name__)
router = APIRouter()

# Dossier temporaire pour stocker uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    auto_index: bool = Query(True, description="Automatically index document (chunking + embeddings)"),
    user_id: str = Query(None, description="User ID who owns this document"),
    organization_id: str = Query(None, description="Organization ID for shared documents")
):
    """
    Upload et parse un document PDF
    
    Args:
        file: Fichier PDF à uploader
        auto_index: Si True, indexe automatiquement (chunking + embeddings)
        user_id: ID de l'utilisateur propriétaire (pour documents personnels)
        organization_id: ID de l'organisation (pour documents partagés)
    
    Returns:
        - filename: Nom du fichier
        - size: Taille en bytes
        - text_preview: Aperçu du texte extrait
        - page_count: Nombre de pages
        - indexed: Si le document a été indexé
        - document_id: ID du document si indexé
        - chunks_count: Nombre de chunks si indexé
    """
    # Vérifier que c'est bien un PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    # Sauvegarder le fichier temporairement
    file_path = UPLOAD_DIR / file.filename
    
    try:
        # Écrire le fichier sur disque
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_size = len(content)
        logger.info(f"Fichier sauvegardé : {file.filename} ({file_size} bytes)")
        
        # Parser le PDF - Méthode 1: pypdf (plus rapide)
        extracted_text = ""
        page_count = 0
        
        try:
            with open(file_path, "rb") as pdf_file:
                pdf_reader = pypdf.PdfReader(pdf_file)
                page_count = len(pdf_reader.pages)
                
                # Extraire texte de toutes les pages
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
                
                logger.info(f"pypdf: {page_count} pages, {len(extracted_text)} caractères")
        
        except Exception as e:
            logger.warning(f"pypdf a échoué, tentative avec pdfplumber: {e}")
            
            # Fallback: pdfplumber (plus robuste pour PDFs complexes)
            try:
                with pdfplumber.open(file_path) as pdf:
                    page_count = len(pdf.pages)
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n"
                    
                    logger.info(f"pdfplumber: {page_count} pages, {len(extracted_text)} caractères")
            
            except Exception as e2:
                logger.error(f"Échec parsing PDF: {e2}")
                raise HTTPException(status_code=500, detail="Impossible de parser le PDF")
        
        # Nettoyer le texte
        extracted_text = extracted_text.strip()
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Aucun texte trouvé dans le PDF (PDF image?)")
        
        # Preview (500 premiers caractères)
        text_preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
        
        logger.info(f"✅ PDF parsé avec succès: {file.filename}")
        
        # Préparer la réponse de base
        response = {
            "success": True,
            "filename": file.filename,
            "size_bytes": file_size,
            "page_count": page_count,
            "text_length": len(extracted_text),
            "text_preview": text_preview,
            "file_path": str(file_path),
            "indexed": False
        }
        
        # Si auto_index activé, indexer le document
        if auto_index:
            try:
                logger.info(f"🚀 Indexation automatique activée pour {file.filename}")
                
                # Obtenir le VectorStore
                vector_store = get_vector_store()
                
                # Stocker document + chunks + embeddings
                document_id = vector_store.store_document(
                    filename=file.filename,
                    content=extracted_text,
                    file_path=str(file_path),
                    file_type="pdf",
                    file_size=file_size,
                    page_count=page_count,
                    scope="organization" if organization_id else "user",
                    user_id=user_id,
                    organization_id=organization_id
                )
                
                response["indexed"] = True
                response["document_id"] = document_id
                response["message"] = f"Document uploadé et indexé avec succès ({page_count} pages)"
                
                logger.info(f"✅ Document {file.filename} indexé: {document_id}")
            
            except Exception as e:
                logger.error(f"❌ Erreur indexation: {e}")
                response["indexed"] = False
                response["indexing_error"] = str(e)
                response["message"] = "Document uploadé mais erreur lors de l'indexation"
        
        return response
    
    except HTTPException:
        # Re-raise les erreurs HTTP
        raise
    
    except Exception as e:
        logger.error(f"Erreur upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.get("/documents")
async def list_documents(
    user_id: str = Query(None, description="Filter by user ID"),
    organization_id: str = Query(None, description="Filter by organization ID")
):
    """Liste tous les documents uploadés depuis la base de données"""
    try:
        from utils.database import SessionLocal
        from sqlalchemy import text
        
        with SessionLocal() as db:
            # Récupérer les documents :
            # - Documents publics (scope='organization') de l'organisation de l'utilisateur
            # - Documents personnels (scope='user') appartenant à l'utilisateur
            query = text("""
                SELECT 
                    filename,
                    file_size,
                    EXTRACT(EPOCH FROM uploaded_at) as uploaded_at,
                    is_indexed,
                    scope
                FROM documents
                WHERE (
                    (scope = 'organization' AND organization_id = :org_id)
                    OR (scope = 'user' AND user_id = :user_id)
                )
                ORDER BY uploaded_at DESC
            """)
            
            result = db.execute(query, {
                "org_id": organization_id,
                "user_id": user_id
            })
            files = []
            
            for row in result:
                files.append({
                    "filename": row[0],
                    "file_size": row[1],
                    "uploaded_at": row[2],
                    "is_indexed": row[3],
                    "scope": row[4]
                })
        
        return {
            "success": True,
            "count": len(files),
            "documents": files
        }
    
    except Exception as e:
        logger.error(f"Erreur liste documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{filename}")
async def delete_document(
    filename: str, 
    user_id: str = Query(None, description="User ID for ownership check"),
    role: str = Query(None, description="User role (ADMIN or MEMBER)")
):
    """Supprime un document uploadé de la base et du disque avec vérification des permissions"""
    from utils.database import SessionLocal
    from sqlalchemy import text
    
    try:
        with SessionLocal() as db:
            # Vérifier si le document existe et récupérer ses infos
            check_query = text("""
                SELECT id, file_path, user_id, organization_id, scope 
                FROM documents 
                WHERE filename = :filename
            """)
            result = db.execute(check_query, {"filename": filename}).fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Document non trouvé dans la base de données")
            
            document_id = result[0]
            file_path_db = result[1]
            doc_user_id = result[2]
            doc_org_id = result[3]
            doc_scope = result[4]
            
            # Vérification des permissions
            can_delete = False
            
            # Cas 1: Document personnel -> seul le propriétaire peut supprimer
            if doc_scope == "user" and doc_user_id == user_id:
                can_delete = True
            
            # Cas 2: Document d'organisation -> seul un ADMIN peut supprimer
            elif doc_scope == "organization" and role == "ADMIN":
                can_delete = True
            
            if not can_delete:
                raise HTTPException(
                    status_code=403, 
                    detail="Vous n'avez pas les permissions pour supprimer ce document"
                )
            
            # Supprimer les chunks associés (CASCADE devrait le faire mais soyons explicites)
            delete_chunks_query = text("DELETE FROM document_chunks WHERE document_id = :document_id")
            db.execute(delete_chunks_query, {"document_id": document_id})
            
            # Supprimer le document de la base
            delete_doc_query = text("DELETE FROM documents WHERE id = :document_id")
            db.execute(delete_doc_query, {"document_id": document_id})
            db.commit()
            
            logger.info(f"Document supprimé de la DB: {filename} (user: {user_id}, role: {role})")
        
        # Supprimer le fichier du disque
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            os.remove(file_path)
            logger.info(f"Fichier supprimé du disque: {filename}")
        
        return {
            "success": True,
            "message": f"Document {filename} supprimé"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression: {e}")
        raise HTTPException(status_code=500, detail=str(e))

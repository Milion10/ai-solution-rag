"""
Module de découpage (chunking) de texte
Utilise RecursiveCharacterTextSplitter de LangChain pour un découpage intelligent
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """
    Découpe des documents en chunks intelligents
    """
    
    def __init__(
        self,
        chunk_size: int = 800,  # Taille en tokens
        chunk_overlap: int = 200,  # Overlap pour contexte
        separators: List[str] = None
    ):
        """
        Initialise le chunker
        
        Args:
            chunk_size: Taille maximale d'un chunk en caractères
            chunk_overlap: Nombre de caractères de chevauchement
            separators: Séparateurs pour le découpage (par défaut: paragraphes, phrases, espaces)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Séparateurs par défaut: priorité paragraphe > phrase > mot
        if separators is None:
            separators = [
                "\n\n",  # Paragraphes
                "\n",    # Lignes
                ". ",    # Phrases
                ", ",    # Virgules
                " ",     # Mots
                ""       # Caractères (fallback)
            ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
        
        logger.info(f"TextChunker initialisé: size={chunk_size}, overlap={chunk_overlap}")
    
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Découpe un texte en chunks
        
        Args:
            text: Texte à découper
            metadata: Métadonnées optionnelles à ajouter à chaque chunk
        
        Returns:
            Liste de dictionnaires avec 'content', 'chunk_index', 'metadata'
        """
        if not text or not text.strip():
            logger.warning("Texte vide fourni au chunker")
            return []
        
        # Découper avec LangChain
        chunks = self.splitter.split_text(text)
        
        logger.info(f"Texte découpé en {len(chunks)} chunks (avg size: {len(text)//len(chunks) if chunks else 0} chars)")
        
        # Formater les chunks avec métadonnées
        result = []
        for idx, chunk_text in enumerate(chunks):
            chunk_data = {
                "content": chunk_text,
                "chunk_index": idx,
                "char_count": len(chunk_text),
                "metadata": metadata or {}
            }
            result.append(chunk_data)
        
        return result
    
    
    def chunk_document(
        self,
        text: str,
        document_id: str = None,
        filename: str = None,
        page_count: int = None
    ) -> List[Dict]:
        """
        Découpe un document avec métadonnées enrichies
        
        Args:
            text: Contenu du document
            document_id: ID unique du document
            filename: Nom du fichier
            page_count: Nombre de pages
        
        Returns:
            Liste de chunks avec métadonnées
        """
        metadata = {
            "document_id": document_id,
            "filename": filename,
            "page_count": page_count,
            "total_chars": len(text)
        }
        
        chunks = self.chunk_text(text, metadata)
        
        logger.info(f"Document '{filename}' découpé: {len(chunks)} chunks")
        
        return chunks


# Instance globale (singleton)
_chunker_instance = None

def get_chunker() -> TextChunker:
    """Retourne l'instance singleton du chunker"""
    global _chunker_instance
    if _chunker_instance is None:
        _chunker_instance = TextChunker()
    return _chunker_instance


if __name__ == "__main__":
    # Test du chunker
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    
    test_text = """
    L'intelligence artificielle (IA) est un domaine de l'informatique qui vise à créer des machines capables de réaliser des tâches nécessitant normalement l'intelligence humaine.
    
    Les systèmes d'IA peuvent apprendre, raisonner, percevoir et prendre des décisions. Le machine learning est une branche importante de l'IA.
    
    Les applications de l'IA sont nombreuses: reconnaissance vocale, vision par ordinateur, traduction automatique, véhicules autonomes, etc.
    """
    
    chunks = chunker.chunk_text(test_text, metadata={"source": "test"})
    
    print(f"\n📄 Texte original: {len(test_text)} caractères")
    print(f"✂️  Découpé en {len(chunks)} chunks:\n")
    
    for chunk in chunks:
        print(f"Chunk {chunk['chunk_index']}: {chunk['char_count']} chars")
        print(f"  {chunk['content'][:100]}...")
        print()

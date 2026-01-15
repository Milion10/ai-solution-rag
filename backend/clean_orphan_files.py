"""
Script pour nettoyer les fichiers orphelins dans uploads/
(fichiers qui existent sur le disque mais pas dans la DB)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from utils.database import SessionLocal
from sqlalchemy import text

UPLOAD_DIR = Path("uploads")

def clean_orphan_files():
    """Supprime les fichiers qui ne sont pas dans la base de données"""
    
    with SessionLocal() as db:
        # Récupérer tous les fichiers de la DB
        query = text("SELECT filename FROM documents")
        result = db.execute(query)
        db_files = {row[0] for row in result}
    
    # Lister tous les fichiers sur le disque
    disk_files = {f.name for f in UPLOAD_DIR.glob("*.pdf")}
    
    # Trouver les orphelins
    orphans = disk_files - db_files
    
    if not orphans:
        print("✅ Aucun fichier orphelin trouvé")
        return
    
    print(f"🗑️  {len(orphans)} fichier(s) orphelin(s) trouvé(s):")
    for filename in orphans:
        print(f"   - {filename}")
    
    confirm = input("\n❓ Voulez-vous les supprimer? (oui/non): ")
    if confirm.lower() in ['oui', 'o', 'yes', 'y']:
        for filename in orphans:
            file_path = UPLOAD_DIR / filename
            file_path.unlink()
            print(f"   ✅ Supprimé: {filename}")
        print(f"\n✨ {len(orphans)} fichier(s) nettoyé(s)")
    else:
        print("❌ Annulé")

if __name__ == "__main__":
    clean_orphan_files()

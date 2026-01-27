"""
Connexion et gestion de la base de données PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import configuration centralisée
try:
    from config import settings
    DATABASE_URL = settings.database_url
except ImportError:
    # Fallback si config.py pas trouvé (tests isolés)
    import os
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ai_user:change-me-in-production@localhost:5432/ai_solution")

# Créer engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérifier connexion avant utilisation
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour modèles SQLAlchemy
Base = declarative_base()


def get_db():
    """
    Dependency pour obtenir une session DB
    Usage avec FastAPI: Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test de connexion à la base de données"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connexion PostgreSQL réussie!")
            return True
    except Exception as e:
        print(f"❌ Erreur connexion PostgreSQL: {e}")
        return False


if __name__ == "__main__":
    test_connection()

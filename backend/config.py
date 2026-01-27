"""
Configuration centralisée de l'application
Utilise Pydantic Settings pour validation et gestion des variables d'environnement
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional, Literal
import secrets
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Configuration centralisée avec validation automatique.
    Toutes les valeurs sont chargées depuis .env
    """
    
    # ===========================================
    # DATABASE
    # ===========================================
    database_url: str = Field(
        default="postgresql://ai_user:change-me-in-production@localhost:5432/ai_solution",
        description="URL de connexion PostgreSQL"
    )
    
    # ===========================================
    # REDIS
    # ===========================================
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="URL de connexion Redis"
    )
    
    # ===========================================
    # MINIO (Stockage fichiers)
    # ===========================================
    minio_endpoint: str = Field(
        default="localhost:9000",
        description="Endpoint MinIO"
    )
    minio_access_key: str = Field(
        default="minioadmin",
        description="Access key MinIO"
    )
    minio_secret_key: str = Field(
        default="minioadmin",
        description="Secret key MinIO"
    )
    minio_bucket_name: str = Field(
        default="ai-documents",
        description="Nom du bucket MinIO"
    )
    
    # ===========================================
    # SECURITY
    # ===========================================
    jwt_secret: str = Field(
        default="your-secret-key-change-in-production",
        description="Clé secrète JWT (DOIT être changée en production !)"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Algorithme JWT"
    )
    jwt_expiration_hours: int = Field(
        default=24,
        description="Durée de validité du JWT en heures"
    )
    
    # ===========================================
    # AI / LLM
    # ===========================================
    llm_provider: Literal["ollama", "groq"] = Field(
        default="ollama",
        description="Provider LLM: 'ollama' (local) ou 'groq' (cloud)"
    )
    
    # Ollama (Local)
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="URL de base Ollama"
    )
    ollama_model: str = Field(
        default="mistral:7b-instruct",
        description="Modèle Ollama à utiliser"
    )
    
    # Groq (Cloud)
    groq_api_key: Optional[str] = Field(
        default=None,
        description="Clé API Groq (requis si llm_provider=groq)"
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Modèle Groq à utiliser"
    )
    
    # Embeddings
    embeddings_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Modèle sentence-transformers pour embeddings"
    )
    
    # Legacy (pour compatibilité)
    llm_model_path: Optional[str] = Field(
        default=None,
        description="Chemin vers modèle GGUF (legacy, non utilisé)"
    )
    
    # ===========================================
    # SERVER
    # ===========================================
    host: str = Field(
        default="0.0.0.0",
        description="Adresse d'écoute du serveur"
    )
    port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="Port du serveur (8000 par défaut)"
    )
    debug: bool = Field(
        default=False,
        description="Mode debug (True en développement)"
    )
    
    # ===========================================
    # RAG PARAMETERS
    # ===========================================
    chunk_size: int = Field(
        default=800,
        ge=100,
        le=2000,
        description="Taille des chunks de texte (tokens)"
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        le=500,
        description="Overlap entre chunks (tokens)"
    )
    top_k_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Nombre de chunks à récupérer pour RAG"
    )
    similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Seuil de similarité cosine"
    )
    
    # ===========================================
    # LOGGING
    # ===========================================
    log_level: str = Field(
        default="INFO",
        description="Niveau de log: DEBUG, INFO, WARNING, ERROR"
    )
    
    # Configuration Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore les variables d'env non définies
    )
    
    # ===========================================
    # VALIDATORS
    # ===========================================
    
    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Valide que le JWT secret a été changé en production"""
        insecure_values = [
            "your-secret-key-change-in-production",
            "changeme",
            "secret",
            "password"
        ]
        
        if v.lower() in insecure_values:
            logger.warning(
                "⚠️  JWT_SECRET utilise une valeur par défaut non sécurisée ! "
                "Générez un secret fort avec: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        
        if len(v) < 32:
            logger.warning(
                f"⚠️  JWT_SECRET trop court ({len(v)} caractères). "
                "Recommandé: 32+ caractères"
            )
        
        return v
    
    @field_validator("groq_api_key")
    @classmethod
    def validate_groq_api_key(cls, v: Optional[str], info) -> Optional[str]:
        """Valide que la clé Groq est présente si provider=groq"""
        # Note: info.data contient les autres champs déjà validés
        llm_provider = info.data.get("llm_provider")
        
        if llm_provider == "groq" and not v:
            raise ValueError(
                "GROQ_API_KEY est requis quand LLM_PROVIDER=groq. "
                "Obtenez une clé sur https://console.groq.com"
            )
        
        return v
    
    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """Valide que overlap < chunk_size"""
        chunk_size = info.data.get("chunk_size", 800)
        
        if v >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({v}) doit être < chunk_size ({chunk_size})"
            )
        
        return v
    
    # ===========================================
    # HELPER METHODS
    # ===========================================
    
    def get_cors_origins(self) -> list[str]:
        """Retourne les origines CORS autorisées selon l'environnement"""
        if self.debug:
            # Développement: autoriser localhost
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]
        else:
            # Production: whitelist explicite (à configurer via env var)
            # TODO: Ajouter CORS_ORIGINS dans .env
            return ["https://votre-domaine.com"]
    
    def get_log_level(self) -> int:
        """Convertit le niveau de log en constante logging"""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return levels.get(self.log_level.upper(), logging.INFO)
    
    def generate_secure_secret(self) -> str:
        """Génère un secret cryptographiquement sécurisé"""
        return secrets.token_urlsafe(32)
    
    def display_config_summary(self) -> None:
        """Affiche un résumé de la configuration au démarrage"""
        print("\n" + "="*60)
        print("⚙️  CONFIGURATION APPLICATION")
        print("="*60)
        print(f"🌐 Server:        {self.host}:{self.port}")
        print(f"🐛 Debug:         {self.debug}")
        print(f"🤖 LLM Provider:  {self.llm_provider}")
        
        if self.llm_provider == "groq":
            print(f"   ├─ Model:      {self.groq_model}")
            print(f"   └─ API Key:    {'✓ Configurée' if self.groq_api_key else '✗ Manquante'}")
        else:
            print(f"   ├─ Base URL:   {self.ollama_base_url}")
            print(f"   └─ Model:      {self.ollama_model}")
        
        print(f"📊 Embeddings:    {self.embeddings_model}")
        print(f"📦 Database:      {self.database_url.split('@')[-1]}")  # Cache les credentials
        print(f"🔐 JWT:           {self.jwt_algorithm} ({self.jwt_expiration_hours}h)")
        print(f"📝 Log Level:     {self.log_level}")
        print(f"🔍 RAG:")
        print(f"   ├─ Chunk size: {self.chunk_size}")
        print(f"   ├─ Overlap:    {self.chunk_overlap}")
        print(f"   ├─ Top-K:      {self.top_k_results}")
        print(f"   └─ Threshold:  {self.similarity_threshold}")
        print("="*60 + "\n")


# ===========================================
# INSTANCE GLOBALE
# ===========================================

# Charger la config une seule fois au démarrage
settings = Settings()

# Afficher warnings si nécessaire
if settings.debug:
    logger.info("🐛 Mode DEBUG activé")

if settings.jwt_secret in ["your-secret-key-change-in-production", "changeme"]:
    logger.error(
        "🔴 SÉCURITÉ: JWT_SECRET doit être changé avant le déploiement en production !\n"
        f"   Générez un secret: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )


# ===========================================
# HELPER POUR TESTS
# ===========================================

def get_settings() -> Settings:
    """
    Retourne l'instance de configuration.
    Permet de mocker facilement dans les tests.
    """
    return settings


if __name__ == "__main__":
    # Test de la configuration
    settings.display_config_summary()
    
    print("✅ Configuration chargée avec succès !")
    print(f"\n💡 Pour générer un nouveau JWT_SECRET:")
    print(f"   {settings.generate_secure_secret()}")

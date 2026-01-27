"""
FastAPI Backend - AI Solution
Point d'entrée principal de l'API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import de la configuration centralisée
from config import settings

# Configuration logging avec niveau depuis config
logging.basicConfig(
    level=settings.get_log_level(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Afficher résumé de configuration au démarrage
if settings.debug:
    settings.display_config_summary()

# Initialisation FastAPI
app = FastAPI(
    title="AI Solution API",
    description="API REST pour solution IA conversationnelle on-premise",
    version="0.1.0-poc",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug
)

# Configuration CORS avec origines depuis config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint racine - Informations API"""
    return {
        "message": "AI Solution API",
        "version": "0.1.0-poc",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-solution-backend"
    }


# Import et inclusion des routers
from api import documents, search, chat

app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Démarrage serveur sur {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

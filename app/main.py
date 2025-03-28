from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import bluetooth, session

# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Configuration CORS pour permettre les requêtes depuis Claude
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers API
app.include_router(bluetooth.router)
app.include_router(session.router)

# Route de vérification de l'état du serveur
@app.get("/health")
async def health_check():
    """
    Route simple pour vérifier que le serveur fonctionne
    """
    return {"status": "ok"}
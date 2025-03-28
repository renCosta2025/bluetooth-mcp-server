import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Démarrage du serveur avec les paramètres de configuration
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST, 
        port=settings.PORT,
        reload=settings.DEBUG
    )
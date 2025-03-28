import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

class Settings(BaseSettings):
    """Configuration de l'application"""
    # Nom de l'application
    APP_NAME: str = "Bluetooth MCP Server"
    
    # Mode de débogage
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configuration CORS
    CORS_ORIGINS: list = ["*"]
    
    # Port du serveur
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Host du serveur
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    class Config:
        env_file = ".env"

# Création d'une instance des paramètres
settings = Settings()
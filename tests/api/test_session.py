import pytest
from fastapi.testclient import TestClient
import uuid
from unittest.mock import patch

# Import de l'application FastAPI
from app.main import app

# Création d'un client de test
client = TestClient(app)

def test_create_session_endpoint():
    """Test pour vérifier que l'endpoint /mcp/v1/session fonctionne correctement"""
    # Mock de uuid pour avoir un ID prévisible
    with patch('uuid.uuid4', return_value=uuid.UUID('12345678-1234-5678-1234-567812345678')):
        # Appel de l'endpoint
        response = client.post("/mcp/v1/session")
        
        # Vérifications
        assert response.status_code == 200
        data = response.json()
        
        # Vérification de la structure de la réponse
        assert "session" in data
        assert "tools" in data
        
        # Vérification de l'ID de session
        assert data["session"]["id"] == "bluetooth-session-12345678-1234-5678-1234-567812345678"
        
        # Vérification des outils disponibles
        assert len(data["tools"]) == 1
        assert data["tools"][0]["name"] == "bluetooth-scan"
        
        # Vérification du schéma de l'outil
        tool = data["tools"][0]
        assert "description" in tool
        assert "parameters" in tool
        assert "properties" in tool["parameters"]
        assert "duration" in tool["parameters"]["properties"]
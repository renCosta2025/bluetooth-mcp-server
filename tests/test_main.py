from fastapi.testclient import TestClient
from app.main import app

# Création d'un client de test
client = TestClient(app)

def test_health_check():
    """Test pour vérifier que la route /health fonctionne correctement"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
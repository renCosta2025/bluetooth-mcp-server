import pytest
from pydantic import ValidationError

def test_session_response_model():
    """Test pour vérifier que le modèle SessionResponse fonctionne correctement"""
    # Importation du modèle
    from app.models.session import SessionResponse
    
    # Test avec des données valides
    session_data = {
        "session": {"id": "test-session-123"},
        "tools": [
            {
                "name": "bluetooth-scan",
                "description": "Scans for nearby Bluetooth devices",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "duration": {
                            "type": "number",
                            "description": "Scan duration in seconds"
                        }
                    }
                }
            }
        ]
    }
    
    session_response = SessionResponse(**session_data)
    assert session_response.session["id"] == "test-session-123"
    assert len(session_response.tools) == 1
    assert session_response.tools[0]["name"] == "bluetooth-scan"
    
    # Test avec session invalide (sans id)
    invalid_data = {
        "session": {},
        "tools": []
    }
    
    with pytest.raises(ValidationError):
        SessionResponse(**invalid_data)
    
    # Test avec des outils vides (devrait être valide)
    empty_tools_data = {
        "session": {"id": "test-session-123"},
        "tools": []
    }
    
    empty_tools_response = SessionResponse(**empty_tools_data)
    assert empty_tools_response.session["id"] == "test-session-123"
    assert len(empty_tools_response.tools) == 0
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

# Import de l'application FastAPI
from app.main import app

# Création d'un client de test
client = TestClient(app)

def test_bluetooth_scan_endpoint():
    """Test pour vérifier que l'endpoint /mcp/v1/tools/bluetooth-scan fonctionne correctement"""
    # Import des modèles pour créer nos données de test
    from app.models.bluetooth import BluetoothDevice
    
    # Création de mock devices pour le test
    mock_devices = [
        BluetoothDevice(
            id="00:11:22:33:44:55",
            address="00:11:22:33:44:55",
            name="Device 1",
            rssi=-65
        ),
        BluetoothDevice(
            id="AA:BB:CC:DD:EE:FF",
            address="AA:BB:CC:DD:EE:FF",
            name="Device 2",
            rssi=-80
        )
    ]
    
    # Patch du service Bluetooth pour éviter d'effectuer un vrai scan
    with patch('app.api.bluetooth.bluetooth_service.scan_for_devices') as mock_scan:
        # Configuration du mock pour renvoyer nos appareils de test
        mock_scan.return_value = mock_devices
        
        # Appel de l'endpoint
        response = client.post(
            "/mcp/v1/tools/bluetooth-scan",
            json={"duration": 3.0, "filter_name": None}
        )
        
        # Vérifications
        assert response.status_code == 200
        data = response.json()
        assert "devices" in data
        assert len(data["devices"]) == 2
        assert data["devices"][0]["name"] == "Device 1"
        assert data["devices"][1]["name"] == "Device 2"
        
        # Vérification que le service a été appelé avec les bons paramètres
        mock_scan.assert_called_once_with(duration=3.0, filter_name=None)

def test_bluetooth_scan_with_filter():
    """Test de l'endpoint de scan avec un filtre sur le nom"""
    # Import des modèles pour créer nos données de test
    from app.models.bluetooth import BluetoothDevice
    
    # Création d'un seul appareil qui correspond au filtre
    mock_devices = [
        BluetoothDevice(
            id="00:11:22:33:44:55",
            address="00:11:22:33:44:55",
            name="Device 1",
            rssi=-65
        )
    ]
    
    # Patch du service Bluetooth
    with patch('app.api.bluetooth.bluetooth_service.scan_for_devices') as mock_scan:
        # Configuration du mock
        mock_scan.return_value = mock_devices
        
        # Appel de l'endpoint avec un filtre
        response = client.post(
            "/mcp/v1/tools/bluetooth-scan",
            json={"duration": 5.0, "filter_name": "Device 1"}
        )
        
        # Vérifications
        assert response.status_code == 200
        data = response.json()
        assert len(data["devices"]) == 1
        assert data["devices"][0]["name"] == "Device 1"
        
        # Vérification que le service a été appelé avec les bons paramètres
        mock_scan.assert_called_once_with(duration=5.0, filter_name="Device 1")

def test_bluetooth_scan_error():
    """Test de la gestion des erreurs dans l'endpoint de scan"""
    # Import de l'exception personnalisée
    from app.services.bluetooth_service import BluetoothScanError
    
    # Patch du service Bluetooth pour simuler une erreur
    with patch('app.api.bluetooth.bluetooth_service.scan_for_devices') as mock_scan:
        # Configuration du mock pour lever une exception
        mock_scan.side_effect = BluetoothScanError("Test error")
        
        # Appel de l'endpoint
        response = client.post(
            "/mcp/v1/tools/bluetooth-scan",
            json={"duration": 5.0}
        )
        
        # Vérification que l'erreur est bien gérée
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Test error" in data["detail"]
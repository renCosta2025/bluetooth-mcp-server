import pytest
from pydantic import ValidationError

def test_bluetooth_device_model():
    """Test pour vérifier que le modèle BluetoothDevice fonctionne correctement"""
    # Importation du modèle
    from app.models.bluetooth import BluetoothDevice
    
    # Test avec des données valides
    device_data = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "Test Device",
        "rssi": -65
    }
    
    device = BluetoothDevice(**device_data)
    assert device.id == "00:11:22:33:44:55"
    assert device.address == "00:11:22:33:44:55"
    assert device.name == "Test Device"
    assert device.rssi == -65
    
    # Test avec des données invalides (rssi comme chaîne)
    invalid_data = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "Test Device",
        "rssi": "invalid"
    }
    
    with pytest.raises(ValidationError):
        BluetoothDevice(**invalid_data)

def test_bluetooth_scan_params_model():
    """Test pour vérifier que le modèle BluetoothScanParams fonctionne correctement"""
    # Importation du modèle
    from app.models.bluetooth import BluetoothScanParams
    
    # Test avec les valeurs par défaut
    params = BluetoothScanParams()
    assert params.duration == 5.0
    assert params.filter_name is None
    
    # Test avec des valeurs personnalisées
    custom_params = BluetoothScanParams(duration=10.0, filter_name="Test")
    assert custom_params.duration == 10.0
    assert custom_params.filter_name == "Test"
    
    # Test avec une durée négative (devrait échouer)
    with pytest.raises(ValidationError):
        BluetoothScanParams(duration=-1.0)

def test_scan_response_model():
    """Test pour vérifier que le modèle ScanResponse fonctionne correctement"""
    # Importation des modèles
    from app.models.bluetooth import ScanResponse, BluetoothDevice
    
    # Création de quelques appareils pour le test
    device1 = BluetoothDevice(
        id="00:11:22:33:44:55",
        address="00:11:22:33:44:55",
        name="Device 1",
        rssi=-65
    )
    
    device2 = BluetoothDevice(
        id="AA:BB:CC:DD:EE:FF",
        address="AA:BB:CC:DD:EE:FF",
        name="Device 2",
        rssi=-80
    )
    
    # Création d'une réponse de scan
    scan_response = ScanResponse(devices=[device1, device2])
    
    # Vérification
    assert len(scan_response.devices) == 2
    assert scan_response.devices[0].name == "Device 1"
    assert scan_response.devices[1].name == "Device 2"
    
    # Test avec une liste vide
    empty_response = ScanResponse(devices=[])
    assert len(empty_response.devices) == 0
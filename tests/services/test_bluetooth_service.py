import pytest
import asyncio
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_scan_for_devices():
    """Test pour vérifier que la fonction scan_for_devices fonctionne correctement"""
    # Import du service
    from app.services.bluetooth_service import BluetoothService
    
    # Création de mock devices pour le test
    mock_device1 = MagicMock()
    mock_device1.address = "00:11:22:33:44:55"
    mock_device1.name = "Device 1"
    mock_device1.rssi = -65
    
    mock_device2 = MagicMock()
    mock_device2.address = "AA:BB:CC:DD:EE:FF"
    mock_device2.name = "Device 2"
    mock_device2.rssi = -80
    
    # Mock pour BleakScanner.discover
    with patch('app.services.bluetooth_service.BleakScanner') as mock_scanner:
        # Configuration du mock pour renvoyer nos appareils de test
        mock_scanner.discover.return_value = [mock_device1, mock_device2]
        
        # Instanciation du service
        service = BluetoothService()
        
        # Test du scan standard
        devices = await service.scan_for_devices(duration=5.0)
        
        # Vérification que BleakScanner.discover a été appelé avec la bonne durée
        mock_scanner.discover.assert_called_once_with(timeout=5.0)
        
        # Vérification des résultats
        assert len(devices) == 2
        assert devices[0].address == "00:11:22:33:44:55"
        assert devices[0].name == "Device 1"
        assert devices[1].address == "AA:BB:CC:DD:EE:FF"
        assert devices[1].name == "Device 2"

@pytest.mark.asyncio
async def test_scan_with_filter():
    """Test pour vérifier que le filtrage par nom fonctionne correctement"""
    # Import du service
    from app.services.bluetooth_service import BluetoothService
    
    # Création de mock devices pour le test
    mock_device1 = MagicMock()
    mock_device1.address = "00:11:22:33:44:55"
    mock_device1.name = "Device 1"
    mock_device1.rssi = -65
    
    mock_device2 = MagicMock()
    mock_device2.address = "AA:BB:CC:DD:EE:FF"
    mock_device2.name = "Device 2"
    mock_device2.rssi = -80
    
    # Mock pour BleakScanner.discover
    with patch('app.services.bluetooth_service.BleakScanner') as mock_scanner:
        # Configuration du mock pour renvoyer nos appareils de test
        mock_scanner.discover.return_value = [mock_device1, mock_device2]
        
        # Instanciation du service
        service = BluetoothService()
        
        # Test du scan avec filtre sur le nom
        devices = await service.scan_for_devices(duration=5.0, filter_name="Device 1")
        
        # Vérification que BleakScanner.discover a été appelé avec la bonne durée
        mock_scanner.discover.assert_called_once_with(timeout=5.0)
        
        # Vérification des résultats (seulement Device 1 doit être retourné)
        assert len(devices) == 1
        assert devices[0].address == "00:11:22:33:44:55"
        assert devices[0].name == "Device 1"

@pytest.mark.asyncio
async def test_scan_error_handling():
    """Test pour vérifier la gestion des erreurs lors du scan"""
    # Import du service
    from app.services.bluetooth_service import BluetoothService, BluetoothScanError
    
    # Mock pour BleakScanner.discover
    with patch('app.services.bluetooth_service.BleakScanner') as mock_scanner:
        # Configuration du mock pour lever une exception
        mock_scanner.discover.side_effect = Exception("Test error")
        
        # Instanciation du service
        service = BluetoothService()
        
        # Vérification que l'exception est bien levée et convertie
        with pytest.raises(BluetoothScanError) as excinfo:
            await service.scan_for_devices()
        
        # Vérification du message d'erreur
        assert "Test error" in str(excinfo.value)
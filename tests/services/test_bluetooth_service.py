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

@pytest.mark.asyncio
async def test_duplicate_device_handling():
    """Test pour vérifier que la gestion des appareils en double fonctionne correctement"""
    # Import du service
    from app.services.bluetooth_service import BluetoothService
    from app.models.bluetooth import BluetoothDevice
    
    # Création de mock devices pour le test (ayant des informations complémentaires)
    ble_device = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "Unknown",
        "rssi": -75,
        "manufacturer_data": {76: [0, 22, 1, 1]},
        "service_uuids": ["0000180f-0000-1000-8000-00805f9b34fb"],
        "device_type": "BLE",
        "company_name": "Apple, Inc.",
        "detected_by": "ble_scanner"
    }
    
    classic_device = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "iPhone 13",
        "rssi": -60,
        "device_type": "Classic",
        "detected_by": "classic_scanner"
    }
    
    windows_device = {
        "id": "WIN-PNP-DEVICE",
        "address": "00:11:22:33:44:55",  # Même adresse MAC
        "name": "iPhone",
        "rssi": -70,
        "device_type": "Windows-PnP",
        "detected_by": "windows_pnp"
    }
    
    # Mock pour les différents scanners
    with patch('app.services.bluetooth_service.ble_scanner') as mock_ble_scanner, \
         patch('app.services.bluetooth_service.classic_scanner') as mock_classic_scanner, \
         patch('app.services.bluetooth_service.windows_scanner') as mock_windows_scanner, \
         patch('app.services.bluetooth_service.IS_WINDOWS', return_value=True), \
         patch('app.services.bluetooth_service.CLASSIC_BT_AVAILABLE', return_value=True):
        
        # Configuration des mocks pour renvoyer nos appareils de test
        mock_ble_scanner.scan.return_value = [ble_device]
        mock_classic_scanner.scan.return_value = [classic_device]
        mock_windows_scanner.scan.return_value = [windows_device]
        
        # Instanciation du service
        service = BluetoothService()
        
        # Test du scan avec fusion des doublons
        devices = await service.scan_for_devices(
            duration=5.0,
            include_classic=True,
            extended_freebox_detection=True,
            deduplicate_devices=True
        )
        
        # Vérification qu'un seul appareil est retourné (les doublons sont fusionnés)
        assert len(devices) == 1
        
        # Vérification que les informations ont été correctement fusionnées
        merged_device = devices[0]
        assert merged_device.address == "00:11:22:33:44:55"
        assert merged_device.name == "iPhone 13"  # Le nom le plus informatif est conservé
        assert merged_device.rssi == -60  # Le RSSI le plus fort est conservé
        assert 76 in merged_device.manufacturer_data  # Les données du fabricant sont conservées
        assert "0000180f-0000-1000-8000-00805f9b34fb" in merged_device.service_uuids  # Les UUIDs sont conservés
        assert merged_device.detection_sources is not None and len(merged_device.detection_sources) == 3
        assert "ble_scanner" in merged_device.detection_sources
        assert "classic_scanner" in merged_device.detection_sources
        assert "windows_pnp" in merged_device.detection_sources
        
        # Test du scan sans fusion des doublons
        devices_without_dedup = await service.scan_for_devices(
            duration=5.0,
            include_classic=True,
            extended_freebox_detection=True,
            deduplicate_devices=False
        )
        
        # Vérification que trois appareils sont retournés (pas de fusion)
        assert len(devices_without_dedup) == 3
import pytest
from app.utils.bluetooth_utils import (
    format_manufacturer_data,
    format_service_data,
    normalize_mac_address,
    bytes_to_hex_string,
    get_friendly_device_name,
    merge_device_info
)

def test_format_manufacturer_data():
    """Test pour vérifier que format_manufacturer_data fonctionne correctement"""
    # Test avec des données nulles
    assert format_manufacturer_data(None) == {}
    
    # Test avec un dictionnaire vide
    assert format_manufacturer_data({}) == {}
    
    # Test avec des données valides (bytes)
    mfr_data = {76: b'\x01\x02\x03'}
    result = format_manufacturer_data(mfr_data)
    assert result == {76: [1, 2, 3]}
    
    # Test avec des données déjà sous forme de liste
    mfr_data = {76: [1, 2, 3]}
    result = format_manufacturer_data(mfr_data)
    assert result == {76: [1, 2, 3]}

def test_format_service_data():
    """Test pour vérifier que format_service_data fonctionne correctement"""
    # Test avec des données nulles
    assert format_service_data(None) == {}
    
    # Test avec un dictionnaire vide
    assert format_service_data({}) == {}
    
    # Test avec des données valides (bytes)
    svc_data = {"uuid1": b'\x01\x02\x03'}
    result = format_service_data(svc_data)
    assert result == {"uuid1": [1, 2, 3]}
    
    # Test avec des données déjà sous forme de liste
    svc_data = {"uuid1": [1, 2, 3]}
    result = format_service_data(svc_data)
    assert result == {"uuid1": [1, 2, 3]}

def test_normalize_mac_address():
    """Test pour vérifier que normalize_mac_address fonctionne correctement"""
    # Test avec une adresse nulle
    assert normalize_mac_address(None) == ""
    
    # Test avec une adresse vide
    assert normalize_mac_address("") == ""
    
    # Test avec une adresse au format 00:11:22:33:44:55
    assert normalize_mac_address("00:11:22:33:44:55") == "00:11:22:33:44:55"
    
    # Test avec une adresse au format 001122334455
    assert normalize_mac_address("001122334455") == "00:11:22:33:44:55"
    
    # Test avec une adresse au format 00-11-22-33-44-55
    assert normalize_mac_address("00-11-22-33-44-55") == "00:11:22:33:44:55"
    
    # Test avec une adresse au format aléatoire (ne respectant pas le format MAC)
    assert normalize_mac_address("not-a-mac-address") == "not-a-mac-address"
    
    # Test avec une adresse en minuscules
    assert normalize_mac_address("aa:bb:cc:dd:ee:ff") == "AA:BB:CC:DD:EE:FF"

def test_bytes_to_hex_string():
    """Test pour vérifier que bytes_to_hex_string fonctionne correctement"""
    # Test avec des données nulles
    assert bytes_to_hex_string(None) == ""
    
    # Test avec des données vides
    assert bytes_to_hex_string(b'') == ""
    
    # Test avec des données valides
    assert bytes_to_hex_string(b'\x01\x02\x03') == "01 02 03"

def test_get_friendly_device_name():
    """Test pour vérifier que get_friendly_device_name fonctionne correctement"""
    # Test avec un nom déjà significatif
    assert get_friendly_device_name("My Device", "00:11:22:33:44:55") == "My Device"
    
    # Test avec un nom inconnu, pas de données de fabricant (devrait utiliser l'adresse MAC)
    assert get_friendly_device_name("Unknown", "00:11:22:33:44:55") == "BT Device 33:44:55"
    
    # Test avec un nom inconnu mais des données de fabricant Apple
    assert get_friendly_device_name("Unknown", "00:11:22:33:44:55", {76: [1, 2, 3]}) == "Apple, Inc. Device (33:44:55)"

def test_merge_device_info():
    """Test pour vérifier que la fonction merge_device_info fusionne correctement les informations de deux appareils"""
    # Cas 1: Appareil BLE avec plus d'informations et appareil classique avec un nom différent
    ble_device = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "Unknown",
        "rssi": -75,
        "manufacturer_data": {76: [0, 22, 1, 1]},
        "service_uuids": ["0000180f-0000-1000-8000-00805f9b34fb"],
        "service_data": {"0000180f-0000-1000-8000-00805f9b34fb": [0, 1]},
        "tx_power": -59,
        "device_type": "BLE",
        "company_name": "Apple, Inc.",
        "friendly_name": "Apple Device",
        "detected_by": "ble_scanner"
    }
    
    classic_device = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "iPhone 13",
        "rssi": -60,
        "manufacturer_data": {},
        "service_uuids": [],
        "service_data": {},
        "device_type": "Classic",
        "detected_by": "classic_scanner"
    }
    
    merged = merge_device_info(ble_device, classic_device)
    
    # Vérification des informations fusionnées
    assert merged["id"] == "00:11:22:33:44:55"
    assert merged["name"] == "iPhone 13"  # Le nom du classique est prioritaire car plus informatif
    assert merged["rssi"] == -60  # Le RSSI du classique est prioritaire car plus fort
    assert 76 in merged["manufacturer_data"]  # Les données du fabricant sont conservées
    assert "0000180f-0000-1000-8000-00805f9b34fb" in merged["service_uuids"]  # Les UUIDs de service sont conservés
    assert "detection_sources" in merged
    assert "ble_scanner" in merged["detection_sources"]
    assert "classic_scanner" in merged["detection_sources"]
    
    # Cas 2: Fusion de deux appareils Windows avec des informations complémentaires
    windows_device1 = {
        "id": "WIN-PNP-BTHLE-DEV_123456",
        "address": "WIN-PNP-BTHLE-DEV",
        "name": "DaVinci Keyboard",
        "rssi": -65,
        "manufacturer_data": {},
        "service_uuids": [],
        "device_type": "Windows-PnP",
        "company_name": "Unknown (Windows)",
        "friendly_name": "DaVinci Keyboard",
        "detected_by": "windows_pnp",
        "raw_info": "ID: BTHLE\\DEV_123456, Status: OK"
    }
    
    windows_device2 = {
        "id": "WIN-WMI-BTHLE-DEV_123456",
        "address": "WIN-WMI-BTHLE-DEV",
        "name": "DaVinci Keyboard BLE",
        "rssi": -70,
        "manufacturer_data": {},
        "service_uuids": ["0000180a-0000-1000-8000-00805f9b34fb"],
        "device_type": "Windows-WMI",
        "company_name": "Unknown (Windows)",
        "friendly_name": "DaVinci Keyboard",
        "detected_by": "windows_wmi",
        "raw_info": "Registry ID: 123456"
    }
    
    merged_windows = merge_device_info(windows_device1, windows_device2)
    
    # Vérification des informations fusionnées pour les appareils Windows
    assert merged_windows["name"] == "DaVinci Keyboard"  # Le nom le plus court mais plus significatif est conservé
    assert merged_windows["rssi"] == -65  # Le RSSI du premier appareil est plus fort
    assert "0000180a-0000-1000-8000-00805f9b34fb" in merged_windows["service_uuids"]  # Les UUIDs sont ajoutés
    assert "Windows-PnP+Windows-WMI" in merged_windows["device_type"]
    assert "detection_sources" in merged_windows
    assert "windows_pnp" in merged_windows["detection_sources"]
    assert "windows_wmi" in merged_windows["detection_sources"]
    
    # Cas 3: Priorité sur les données avec informations plus riches (sans RSSI disponible)
    device_complete = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "Complete Device",
        "rssi": None,
        "device_type": "BLE",
        "company_name": "Complete Company",
        "friendly_name": "Complete Friendly Name",
        "is_connectable": True,
        "detected_by": "scanner1"
    }
    
    device_partial = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "Unknown",
        "rssi": -80,
        "device_type": "Classic",
        "detected_by": "scanner2"
    }
    
    merged_complete = merge_device_info(device_complete, device_partial, prioritize_high_rssi=False)
    
    assert merged_complete["name"] == "Complete Device"  # Le nom plus informatif est conservé
    assert merged_complete["rssi"] == -80  # Le RSSI disponible est utilisé
    assert merged_complete["company_name"] == "Complete Company"
    assert merged_complete["friendly_name"] == "Complete Friendly Name"
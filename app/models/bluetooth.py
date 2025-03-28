"""
Modèles de données pour les opérations Bluetooth.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union

class BluetoothDevice(BaseModel):
    """Modèle représentant un appareil Bluetooth détecté avec toutes les informations disponibles"""
    id: str
    address: str
    name: str
    rssi: Optional[int] = None
    
    # Informations additionnelles disponibles pendant le scan
    manufacturer_data: Optional[Dict[int, List[int]]] = None
    service_uuids: Optional[List[str]] = None
    service_data: Optional[Dict[str, List[int]]] = None
    tx_power: Optional[int] = None
    appearance: Optional[int] = None
    
    # Informations disponibles après connexion (si demandées)
    connected_info: Optional[Dict[str, Any]] = None
    services: Optional[List[Dict[str, Any]]] = None
    characteristics: Optional[List[Dict[str, Any]]] = None
    
    # Informations déduites
    device_type: Optional[str] = None  # "BLE", "Classic", "BLE+Classic", "Windows-PnP", etc.
    company_name: Optional[str] = None
    is_connectable: Optional[bool] = None
    device_class: Optional[int] = None  # Pour le Bluetooth classique
    major_device_class: Optional[str] = None  # Pour le Bluetooth classique
    minor_device_class: Optional[str] = None  # Pour le Bluetooth classique
    service_classes: Optional[List[str]] = None  # Pour le Bluetooth classique
    friendly_name: Optional[str] = None  # Nom plus convivial basé sur d'autres informations
    
    # Informations de détection
    detected_by: Optional[str] = None  # Méthode de détection principale
    detection_sources: Optional[List[str]] = None  # Toutes les sources de détection
    raw_info: Optional[str] = None  # Informations brutes de détection
    detection_note: Optional[str] = None  # Note sur la détection
    
    # Informations de fusion
    source_id: Optional[str] = None  # ID d'origine avant fusion
    merged_from: Optional[List[str]] = None  # Liste des IDs des appareils fusionnés
    
    # Pour Pydantic v2, utiliser model_config au lieu de Config avec json_schema_extra
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "00:11:22:33:44:55",
                "address": "00:11:22:33:44:55",
                "name": "Device Name",
                "rssi": -65,
                "manufacturer_data": {76: [0, 22, 1, 1, 11, 0]},
                "service_uuids": ["0000180f-0000-1000-8000-00805f9b34fb"],
                "tx_power": -59,
                "device_type": "BLE",
                "company_name": "Apple, Inc.",
                "friendly_name": "iPhone 13",
                "detection_sources": ["ble_scanner", "windows_registry"],
                "merged_from": ["00:11:22:33:44:55", "WIN-REG-001122334455"]
            }
        }
    }

class BluetoothScanParams(BaseModel):
    """Paramètres pour le scan d'appareils Bluetooth"""
    duration: Optional[float] = 5.0
    filter_name: Optional[str] = None
    connect_for_details: Optional[bool] = False  # Si True, tente de se connecter pour plus d'informations
    include_classic: Optional[bool] = True  # Si True, inclut les appareils Bluetooth classiques
    extended_freebox_detection: Optional[bool] = True  # Si True, active la détection spéciale de la Freebox
    deduplicate_devices: Optional[bool] = True  # Si True, fusionne les appareils en double
    parallel_scans: Optional[bool] = True  # Si True, exécute les scans en parallèle pour plus de rapidité
    
    @validator('duration')
    def duration_must_be_positive(cls, v):
        """Validation pour s'assurer que la durée est positive"""
        if v is not None and v <= 0:
            raise ValueError('La durée doit être positive')
        return v
        
    @validator('filter_name')
    def filter_name_null_handling(cls, v):
        """Convertit les valeurs spéciales en None pour le filtre"""
        # Traiter les cas où filter_name est 'null', 'none', une chaîne vide ou 'string'
        if v in [None, 'null', 'none', '', 'string', 'NULL', 'NONE', 'None']:
            return None
        return v

class ScanResponse(BaseModel):
    """Réponse contenant la liste des appareils Bluetooth détectés"""
    devices: List[BluetoothDevice]
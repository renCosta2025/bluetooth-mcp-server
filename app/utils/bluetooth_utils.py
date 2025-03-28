"""
Fonctions utilitaires pour traiter les données Bluetooth.
"""
from typing import Dict, List, Optional, Any
from app.data.company_identifiers import get_company_name
from app.data.mac_prefixes import get_device_info

def format_manufacturer_data(mfr_data: Dict) -> Dict[int, List[int]]:
    """
    Convertit les données du fabricant en un format sérialisable JSON.
    
    Args:
        mfr_data: Dictionnaire des données du fabricant
        
    Returns:
        Dictionnaire formaté pour la sérialisation JSON
    """
    if not mfr_data:
        return {}
    
    result = {}
    for key, value in mfr_data.items():
        # Convertir les bytes en liste d'entiers
        if isinstance(value, bytes):
            result[key] = list(value)
        else:
            result[key] = list(value)
    return result

def format_service_data(svc_data: Dict) -> Dict[str, List[int]]:
    """
    Convertit les données de service en un format sérialisable JSON.
    
    Args:
        svc_data: Dictionnaire des données de service
        
    Returns:
        Dictionnaire formaté pour la sérialisation JSON
    """
    if not svc_data:
        return {}
    
    result = {}
    for key, value in svc_data.items():
        # Convertir les bytes en liste d'entiers
        if isinstance(value, bytes):
            result[key] = list(value)
        else:
            result[key] = list(value)
    return result

def normalize_mac_address(mac_address: str) -> str:
    """
    Normalise une adresse MAC en format standard.
    
    Args:
        mac_address: Adresse MAC à normaliser
        
    Returns:
        Adresse MAC normalisée (XX:XX:XX:XX:XX:XX)
    """
    if not mac_address:
        return ""
        
    # Supprimer tous les séparateurs et convertir en majuscules
    clean_mac = mac_address.upper().replace(':', '').replace('-', '').replace('.', '')
    
    # Vérifier la longueur
    if len(clean_mac) != 12:
        return mac_address  # Retourner l'original si le format est incorrect
    
    # Reformater avec des deux-points
    return ':'.join([clean_mac[i:i+2] for i in range(0, 12, 2)])

def bytes_to_hex_string(data: bytes) -> str:
    """
    Convertit des bytes en une chaîne hexadécimale lisible.
    
    Args:
        data: Données à convertir
        
    Returns:
        Chaîne hexadécimale
    """
    if not data:
        return ""
    return ' '.join([f"{b:02X}" for b in data])

def get_friendly_device_name(device_name: str, mac_address: str, manufacturer_data: Dict = None) -> str:
    """
    Détermine un nom convivial pour l'appareil basé sur diverses sources d'information.
    
    Args:
        device_name: Nom de l'appareil
        mac_address: Adresse MAC de l'appareil
        manufacturer_data: Données du fabricant (optionnel)
        
    Returns:
        Nom convivial de l'appareil
    """
    # Vérifier si le nom de l'appareil est déjà significatif
    if device_name and device_name != "Unknown":
        return device_name
    
    # Essayer de déterminer le nom à partir de l'adresse MAC
    device_info = get_device_info(mac_address)
    if device_info:
        return device_info.get("friendly_name", "")
    
    # Essayer d'obtenir le fabricant à partir des données de fabricant
    company_name = None
    if manufacturer_data:
        for company_id in manufacturer_data.keys():
            company = get_company_name(company_id)
            if company:
                company_name = company
                break
    
    # Construire un nom convivial
    if company_name:
        return f"{company_name} Device ({mac_address[-8:]})"
    
    # Dernière solution : utiliser juste l'adresse MAC
    return f"BT Device {mac_address[-8:]}"

def merge_device_info(ble_device: Dict[str, Any], classic_device: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne les informations de deux appareils (BLE et classique) en un seul appareil.
    Priorise les informations les plus complètes.
    
    Args:
        ble_device: Informations de l'appareil BLE
        classic_device: Informations de l'appareil Bluetooth classique
        
    Returns:
        Informations fusionnées
    """
    if not ble_device:
        return classic_device
    if not classic_device:
        return ble_device
        
    # Copier l'appareil BLE comme base
    merged = ble_device.copy()
    
    # Utiliser les informations de l'appareil classique si manquantes dans BLE
    for key, value in classic_device.items():
        if key not in merged or merged[key] is None or merged[key] == "" or merged[key] == 0:
            merged[key] = value
    
    # Pour certains champs, prendre le plus informatif des deux
    if classic_device.get("name") and classic_device["name"] != "Unknown" and (not merged.get("name") or merged["name"] == "Unknown"):
        merged["name"] = classic_device["name"]
    
    if classic_device.get("friendly_name") and not merged.get("friendly_name"):
        merged["friendly_name"] = classic_device["friendly_name"]
    
    if classic_device.get("company_name") and not merged.get("company_name"):
        merged["company_name"] = classic_device["company_name"]
        
    # Prendre le RSSI le plus fort (plus proche de 0)
    if "rssi" in merged and "rssi" in classic_device:
        merged["rssi"] = max(merged["rssi"], classic_device["rssi"], key=lambda x: abs(x) if x is not None else float('inf'))
    
    # Indiquer que c'est une fusion
    merged["device_type"] = "BLE+Classic"
        
    return merged
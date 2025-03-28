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

def decode_ascii_name(encoded_name: str) -> str:
    """
    Décode une chaîne de caractères représentant des codes ASCII séparés par des espaces.
    
    Args:
        encoded_name: Chaîne encodée (ex: "105 80 104 111 110 101 0")
        
    Returns:
        Chaîne décodée (ex: "iPhone")
    """
    if not encoded_name or not isinstance(encoded_name, str):
        return encoded_name
        
    # Vérifier si la chaîne ressemble à des codes ASCII
    if not all(c.isdigit() or c.isspace() for c in encoded_name):
        return encoded_name
        
    try:
        # Convertir les codes ASCII en caractères
        values = [int(code) for code in encoded_name.split() if code.isdigit()]
        # Arrêter au premier 0 (null terminator)
        if 0 in values:
            values = values[:values.index(0)]
        # Convertir en chaîne de caractères si les valeurs sont dans la plage ASCII imprimable
        decoded = ''.join(chr(code) for code in values if 32 <= code <= 126)
        
        # Retourner la chaîne décodée seulement si elle contient au moins 2 caractères et semble être un nom valide
        if len(decoded) >= 2 and any(c.isalpha() for c in decoded):
            return decoded
        return encoded_name
    except Exception:
        return encoded_name

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
    # Tenter de décoder le nom ASCII si applicable
    if device_name and " " in device_name and all(c.isdigit() or c.isspace() for c in device_name):
        decoded_name = decode_ascii_name(device_name)
        if decoded_name != device_name:
            return decoded_name
            
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

def merge_device_info(ble_device: Dict[str, Any], classic_device: Dict[str, Any], prioritize_high_rssi: bool = True) -> Dict[str, Any]:
    """
    Fusionne les informations de deux appareils (BLE et classique) en un seul appareil.
    Priorise les informations les plus complètes et les signaux les plus forts.
    
    Args:
        ble_device: Informations de l'appareil BLE
        classic_device: Informations de l'appareil Bluetooth classique
        prioritize_high_rssi: Si True, priorise l'appareil avec le RSSI le plus fort
        
    Returns:
        Informations fusionnées
    """
    if not ble_device:
        return classic_device
    if not classic_device:
        return ble_device
    
    # Déterminer quel appareil a le signal le plus fort (RSSI plus proche de 0)
    stronger_device = ble_device
    weaker_device = classic_device
    
    if prioritize_high_rssi and "rssi" in ble_device and "rssi" in classic_device:
        if classic_device["rssi"] is not None and (ble_device["rssi"] is None or abs(classic_device["rssi"]) < abs(ble_device["rssi"])):
            stronger_device = classic_device
            weaker_device = ble_device
    
    # Copier l'appareil avec le signal le plus fort comme base
    merged = stronger_device.copy()
    
    # Utiliser les informations de l'autre appareil si manquantes dans l'appareil principal
    for key, value in weaker_device.items():
        if key not in merged or merged[key] is None or merged[key] == "" or merged[key] == 0 or merged[key] == []:
            merged[key] = value
    
    # Pour certains champs, prendre le plus informatif des deux
    # Fusionner les noms en priorisant les noms significatifs
    
    # Tenter de décoder les noms ASCII encodés
    if weaker_device.get("name") and " " in weaker_device["name"]:
        decoded_name = decode_ascii_name(weaker_device["name"])
        if decoded_name != weaker_device["name"]:
            if not merged.get("name") or merged["name"] == "Unknown":
                merged["name"] = decoded_name
    
    # Nom normal
    if weaker_device.get("name") and weaker_device["name"] != "Unknown" and (not merged.get("name") or merged["name"] == "Unknown"):
        merged["name"] = weaker_device["name"]
    
    # Utiliser le nom convivial le plus informatif
    if weaker_device.get("friendly_name"):
        # Décoder les friendly_names encodés en ASCII
        if " " in weaker_device["friendly_name"]:
            decoded_friendly = decode_ascii_name(weaker_device["friendly_name"])
            if decoded_friendly != weaker_device["friendly_name"]:
                if not merged.get("friendly_name") or "Device" in merged["friendly_name"]:
                    merged["friendly_name"] = decoded_friendly
        
        # Nom convivial normal
        if not merged.get("friendly_name") or len(weaker_device["friendly_name"]) > len(merged["friendly_name"]):
            merged["friendly_name"] = weaker_device["friendly_name"]
    
    # Prendre les informations du fabricant si disponibles
    if weaker_device.get("company_name") and not merged.get("company_name"):
        merged["company_name"] = weaker_device["company_name"]
    
    # Fusionner les manufacturer_data si présents dans les deux appareils
    if "manufacturer_data" in merged and "manufacturer_data" in weaker_device:
        for key, value in weaker_device["manufacturer_data"].items():
            if key not in merged["manufacturer_data"]:
                merged["manufacturer_data"][key] = value
    
    # Fusionner les service_uuids sans doublons
    if "service_uuids" in merged and "service_uuids" in weaker_device and weaker_device["service_uuids"]:
        merged_uuids = set(merged["service_uuids"])
        merged_uuids.update(weaker_device["service_uuids"])
        merged["service_uuids"] = list(merged_uuids)
    
    # Fusionner les service_data
    if "service_data" in merged and "service_data" in weaker_device:
        for key, value in weaker_device["service_data"].items():
            if key not in merged["service_data"]:
                merged["service_data"][key] = value
    
    # Conserver les informations de détection pour traçabilité
    if "detection_sources" not in merged:
        merged["detection_sources"] = []
    
    if merged.get("detected_by") and merged["detected_by"] not in merged["detection_sources"]:
        merged["detection_sources"].append(merged["detected_by"])
    
    if weaker_device.get("detected_by") and weaker_device["detected_by"] not in merged["detection_sources"]:
        merged["detection_sources"].append(weaker_device["detected_by"])
    
    # Conserver les IDs d'origine pour traçabilité
    if "merged_from" not in merged:
        merged["merged_from"] = []
    
    # Ajouter l'ID d'origine si disponible
    if merged.get("source_id") and merged["source_id"] not in merged["merged_from"]:
        merged["merged_from"].append(merged["source_id"])
    
    if weaker_device.get("source_id") and weaker_device["source_id"] not in merged["merged_from"]:
        merged["merged_from"].append(weaker_device["source_id"])
    
    # Si weaker_device a son propre merged_from, fusionner ces IDs également
    if weaker_device.get("merged_from"):
        for source_id in weaker_device["merged_from"]:
            if source_id not in merged["merged_from"]:
                merged["merged_from"].append(source_id)
    
    # Si les merged_from n'ont pas été définis mais que les IDs sont disponibles
    if not merged["merged_from"]:
        if merged.get("id"):
            merged["merged_from"].append(merged["id"])
        if weaker_device.get("id") and weaker_device["id"] != merged.get("id"):
            merged["merged_from"].append(weaker_device["id"])
    
    # Indiquer que c'est une fusion dans le device_type
    if "device_type" in merged and "device_type" in weaker_device and merged["device_type"] != weaker_device["device_type"]:
        types = set()
        if "+" in merged["device_type"]:
            types.update(merged["device_type"].split("+"))
        else:
            types.add(merged["device_type"])
            
        if "+" in weaker_device["device_type"]:
            types.update(weaker_device["device_type"].split("+"))
        else:
            types.add(weaker_device["device_type"])
            
        merged["device_type"] = "+".join(sorted(types))
    
    # Si le weaker_device a des informations de connexion que le merged n'a pas, les ajouter
    if weaker_device.get("connected_info") and not merged.get("connected_info"):
        merged["connected_info"] = weaker_device["connected_info"]
    
    # Si le weaker_device a des services que le merged n'a pas, les ajouter
    if weaker_device.get("services") and not merged.get("services"):
        merged["services"] = weaker_device["services"]
    
    # Si le weaker_device a des caractéristiques que le merged n'a pas, les ajouter
    if weaker_device.get("characteristics") and not merged.get("characteristics"):
        merged["characteristics"] = weaker_device["characteristics"]
    
    return merged
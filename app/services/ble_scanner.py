"""
Module spécialisé pour le scan BLE (Bluetooth Low Energy) avec optimisation pour Windows.
"""
import logging
import asyncio
import platform
from typing import Dict, List, Optional, Any
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from app.utils.bluetooth_utils import (
    format_manufacturer_data,
    format_service_data,
    get_friendly_device_name,
    normalize_mac_address
)
from app.data.company_identifiers import get_company_name
from app.data.mac_prefixes import get_device_info, MAC_PREFIX_DATABASE

# Configurer le logging
logger = logging.getLogger(__name__)

# Vérifier si nous sommes sur Windows
IS_WINDOWS = platform.system() == "Windows"

class BLEScanner:
    """Classe spécialisée dans le scan d'appareils BLE"""
    
    async def scan(self, duration: float = 5.0, filter_name: Optional[str] = None, connect_for_details: bool = False) -> List[Dict[str, Any]]:
        """
        Effectue un scan BLE avec Bleak.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            connect_for_details: Si True, tente de se connecter pour plus d'informations
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils BLE détectés
        """
        discovered_devices_with_ads = {}
        
        def _device_detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
            """Callback pour collecter les appareils et leurs données d'annonce"""
            discovered_devices_with_ads[device.address] = (device, advertisement_data)
            logger.debug(f"Détecté (BLE): {device.address}: {device.name}, RSSI: {advertisement_data.rssi}")
        
        # Démarrer le scanner avec le callback
        logger.debug(f"Démarrage du scan BLE avec durée de {duration} secondes...")
        
        # Sur Windows, augmenter légèrement la durée pour compenser les délais de démarrage
        effective_duration = duration * 1.2 if IS_WINDOWS else duration
        
        scanner = BleakScanner(detection_callback=_device_detection_callback)
        await scanner.start()
        await asyncio.sleep(effective_duration)
        await scanner.stop()
        
        logger.debug(f"Scan BLE terminé. {len(discovered_devices_with_ads)} appareil(s) trouvé(s)")
        
        # Récupérer la liste de prefixes Freebox pour l'analyse
        freebox_prefixes = [prefix.upper().replace(':', '') for prefix, info in MAC_PREFIX_DATABASE.items() 
                          if "Freebox" in info.get("friendly_name", "")]
        
        devices = []
        
        # Si connect_for_details est activé et qu'il y a beaucoup d'appareils, limiter les connexions
        # pour éviter de bloquer trop longtemps
        connection_limit = 5 if len(discovered_devices_with_ads) > 10 else len(discovered_devices_with_ads)
        connected_count = 0
        
        for address, (device, adv_data) in discovered_devices_with_ads.items():
            device_name = device.name or "Unknown"
            
            # Appliquer le filtre si nécessaire
            if filter_name is None or (filter_name.lower() in device_name.lower()):
                # Obtenir les informations du fabricant à partir de l'adresse MAC
                device_info = get_device_info(device.address)
                company_name = device_info.get("company", None) if device_info else None
                
                # Si aucune information d'appareil n'est disponible, essayer à partir des données du fabricant
                if not company_name and adv_data.manufacturer_data:
                    for company_id in adv_data.manufacturer_data.keys():
                        company_name = get_company_name(company_id)
                        if company_name:
                            break
                
                # Sur Windows, vérifier explicitement si c'est une Freebox via l'adresse MAC
                is_freebox = False
                normalized_addr = device.address.upper().replace(':', '')
                for prefix in freebox_prefixes:
                    if normalized_addr.startswith(prefix):
                        is_freebox = True
                        if not device_info:
                            device_info = {
                                "company": "Freebox SA", 
                                "device_type": "Freebox", 
                                "friendly_name": "Freebox Player"
                            }
                        break
                
                # Obtenir un nom convivial
                friendly_name = device_info.get("friendly_name", "") if device_info else get_friendly_device_name(
                    device_name, 
                    device.address, 
                    adv_data.manufacturer_data
                )
                
                # Si c'est une Freebox confirmée mais sans nom, remplacer le nom générique
                if is_freebox and device_name == "Unknown":
                    device_name = "Freebox"
                    if not friendly_name or "Device" in friendly_name:
                        friendly_name = f"Freebox Player ({device.address[-8:]})"
                
                # Construire l'objet de base
                bluetooth_device = {
                    "id": str(device.address),
                    "address": device.address,
                    "name": device_name,
                    "rssi": adv_data.rssi,
                    "manufacturer_data": format_manufacturer_data(adv_data.manufacturer_data),
                    "service_uuids": adv_data.service_uuids or [],
                    "service_data": format_service_data(adv_data.service_data),
                    "tx_power": adv_data.tx_power,
                    "appearance": getattr(adv_data, 'appearance', None),
                    "company_name": company_name or ("Freebox SA" if is_freebox else None),
                    "is_connectable": getattr(adv_data, 'connectable', None),
                    "device_type": "BLE",
                    "friendly_name": friendly_name,
                    "detected_by": "ble_scanner",
                    "is_freebox": is_freebox  # Marqueur spécial pour les Freebox
                }
                
                # Si c'est une Freebox, priorité de connexion
                if is_freebox and connect_for_details:
                    logger.info(f"Freebox détectée à l'adresse {device.address}, tentative de connexion...")
                    connected_count += 1  # Compter même si on dépasse la limite pour les Freebox
                    
                    try:
                        detailed_info = await self._get_detailed_device_info(device)
                        bluetooth_device["connected_info"] = detailed_info.get("info", {})
                        bluetooth_device["services"] = detailed_info.get("services", [])
                        bluetooth_device["characteristics"] = detailed_info.get("characteristics", [])
                        
                        logger.debug(f"Connexion réussie à la Freebox {device.address}")
                    except Exception as e:
                        logger.warning(f"Impossible de se connecter à la Freebox {device.address}: {str(e)}")
                
                # Si demandé et dans la limite, essayer de se connecter pour obtenir plus d'informations
                elif connect_for_details and connected_count < connection_limit:
                    try:
                        logger.debug(f"Tentative de connexion à {device.address}")
                        connected_count += 1
                        
                        detailed_info = await self._get_detailed_device_info(device)
                        bluetooth_device["connected_info"] = detailed_info.get("info", {})
                        bluetooth_device["services"] = detailed_info.get("services", [])
                        bluetooth_device["characteristics"] = detailed_info.get("characteristics", [])
                        
                        logger.debug(f"Connexion réussie à {device.address}")
                    except Exception as e:
                        logger.warning(f"Impossible de se connecter à {device.address}: {str(e)}")
                
                devices.append(bluetooth_device)
        
        logger.debug(f"Après filtrage BLE: {len(devices)} appareil(s) retourné(s)")
        return devices
    
    async def _get_detailed_device_info(self, device: BLEDevice) -> Dict[str, Any]:
        """
        Se connecte à un appareil Bluetooth et récupère des informations détaillées.
        
        Args:
            device: L'appareil BLE à interroger
            
        Returns:
            Dictionnaire contenant des informations détaillées sur l'appareil
        """
        detailed_info = {
            "info": {},
            "services": [],
            "characteristics": []
        }
        
        try:
            # Sur Windows, augmenter le timeout de connexion
            timeout = 15.0 if IS_WINDOWS else 10.0
            
            async with BleakClient(device, timeout=timeout) as client:
                if client.is_connected:
                    # Récupérer les informations générales
                    detailed_info["info"]["connected"] = True
                    detailed_info["info"]["mtu_size"] = client.mtu_size
                    
                    # Récupérer les services
                    services = await client.get_services()
                    for service in services.services.values():
                        service_info = {
                            "uuid": str(service.uuid),
                            "description": service.description,
                            "handle": service.handle
                        }
                        detailed_info["services"].append(service_info)
                        
                        # Si nous détectons des services spécifiques à Freebox, le noter
                        if "Freebox" in service.description or "Free" in service.description:
                            detailed_info["info"]["is_freebox_service"] = True
                        
                        # Récupérer les caractéristiques pour ce service
                        for char in service.characteristics:
                            char_info = {
                                "uuid": str(char.uuid),
                                "description": char.description,
                                "handle": char.handle,
                                "properties": list(char.properties)
                            }
                            
                            # Essayer de lire la valeur si c'est une caractéristique lisible
                            if "read" in char.properties:
                                try:
                                    value = await client.read_gatt_char(char)
                                    char_info["value"] = list(value)
                                    
                                    # Détecter si c'est une caractéristique Freebox
                                    try:
                                        text_value = value.decode('utf-8', errors='ignore')
                                        if "Free" in text_value or "Freebox" in text_value:
                                            detailed_info["info"]["is_freebox_characteristic"] = True
                                    except:
                                        pass
                                        
                                except Exception as e:
                                    char_info["value_error"] = str(e)
                            
                            detailed_info["characteristics"].append(char_info)
        except Exception as e:
            logger.warning(f"Erreur lors de la connexion à {device.address}: {str(e)}")
            detailed_info["info"]["connected"] = False
            detailed_info["info"]["error"] = str(e)
        
        return detailed_info

# Instance singleton pour faciliter l'importation
ble_scanner = BLEScanner()
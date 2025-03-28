"""
Service principal pour la gestion des opérations Bluetooth.
Ce service orchestre l'utilisation des scanners BLE, classique et Windows spécifique.
"""
import logging
import platform
import re
import asyncio
import concurrent.futures
from typing import List, Optional, Dict, Any, Set

from app.models.bluetooth import BluetoothDevice
from app.services.ble_scanner import ble_scanner
from app.services.windows_advanced_scanner import windows_advanced_scanner
from app.services.classic_scanner import classic_scanner, CLASSIC_BT_AVAILABLE
from app.utils.bluetooth_utils import merge_device_info, normalize_mac_address

# Import conditionnel du scanner Windows
IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
    from app.services.windows_scanner import windows_scanner

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Pool d'exécuteurs pour les opérations multithreads
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

class BluetoothScanError(Exception):
    """Exception personnalisée pour les erreurs de scan Bluetooth"""
    pass

class BluetoothService:
    """Service pour gérer les opérations Bluetooth (BLE et classique)"""
    
    async def scan_for_devices(self, 
                         duration: float = 5.0, 
                         filter_name: Optional[str] = None, 
                         connect_for_details: bool = False,
                         include_classic: bool = True,
                         extended_freebox_detection: bool = True,
                         deduplicate_devices: bool = True,
                         parallel_scans: bool = True) -> List[BluetoothDevice]:
        """
        Effectue un scan des appareils Bluetooth à proximité (BLE et classique)
        avec une gestion améliorée des doublons et exécution parallèle
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            connect_for_details: Si True, se connecte à chaque appareil pour plus d'informations
            include_classic: Si True, inclut les appareils Bluetooth classiques
            extended_freebox_detection: Si True, utilise des méthodes spéciales pour détecter la Freebox
            deduplicate_devices: Si True, fusionne les appareils en double
            parallel_scans: Si True, exécute les différents scans en parallèle
            
        Returns:
            Liste des appareils Bluetooth détectés
            
        Raises:
            BluetoothScanError: En cas d'erreur pendant le scan
        """
        try:
            logger.debug(f"Démarrage du scan Bluetooth complet (durée: {duration}s, filtre: {filter_name}, "
                         f"connexion détaillée: {connect_for_details}, Bluetooth classique: {include_classic}, "
                         f"détection Freebox: {extended_freebox_detection}, "
                         f"déduplication: {deduplicate_devices}, "
                         f"scans parallèles: {parallel_scans})")
            
            # Dictionnaire pour stocker tous les appareils découverts
            all_devices = {}
            
            if parallel_scans:
                # Exécution parallèle des différents scans
                tasks = []
                
                # 1. Scan BLE avec Bleak (toujours actif)
                tasks.append(self._ble_scan_task(duration, filter_name, connect_for_details))
                
                # 2. Scan Bluetooth classique (si demandé et disponible)
                if include_classic and CLASSIC_BT_AVAILABLE:
                    tasks.append(self._classic_scan_task(duration, filter_name))
                
                # 3. Sur Windows, scanner spécifique (si demandé)
                if IS_WINDOWS and extended_freebox_detection:
                    tasks.append(self._windows_scan_task(duration, filter_name))
                    
                # 4. Sur Windows, scanner avancé pour détecter plus d'appareils (TV, Freebox, etc.)
                if IS_WINDOWS and extended_freebox_detection:
                    tasks.append(self._windows_advanced_scan_task(duration, filter_name))
                
                # Attendre que tous les scans se terminent
                scan_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Traiter les résultats
                for result in scan_results:
                    if isinstance(result, Exception):
                        logger.error(f"Une méthode de scan a échoué: {str(result)}")
                        continue
                    
                    # Fusionner les appareils détectés
                    for device in result:
                        device_id = device["id"]
                        if deduplicate_devices and device_id in all_devices:
                            all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                        else:
                            all_devices[device_id] = device
            
            else:
                # Exécution séquentielle (ancien comportement)
                
                # 1. Scan BLE avec Bleak
                logger.debug("Démarrage du scan BLE...")
                ble_devices = await ble_scanner.scan(duration, filter_name, connect_for_details)
                
                # Ajouter les appareils BLE au dictionnaire
                for device in ble_devices:
                    device_id = device["id"]
                    device["source_id"] = device_id  # Conserver l'ID d'origine
                    device["detected_by"] = "ble_scanner"
                    
                    if deduplicate_devices:
                        # Vérifier si cet appareil est déjà connu
                        if device_id in all_devices:
                            all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                        else:
                            all_devices[device_id] = device
                    else:
                        # Sans déduplication
                        all_devices[device_id] = device
                
                # 2. Scan Bluetooth classique (si demandé et disponible)
                if include_classic and CLASSIC_BT_AVAILABLE:
                    logger.debug("Démarrage du scan Bluetooth classique...")
                    classic_devices = classic_scanner.scan(duration, filter_name)
                    
                    # Traiter les appareils classiques
                    for device in classic_devices:
                        device_id = device["id"]
                        device["source_id"] = device_id
                        device["detected_by"] = "classic_scanner"
                        
                        if deduplicate_devices:
                            # Vérifier si cet appareil est déjà connu
                            if device_id in all_devices:
                                all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                            else:
                                all_devices[device_id] = device
                        else:
                            # Sans déduplication
                            all_devices[device_id] = device
                    
                elif include_classic and not CLASSIC_BT_AVAILABLE and not IS_WINDOWS:
                    logger.warning("Le module Bluetooth classique n'est pas disponible. "
                                   "Installation recommandée: pip install pybluez2")
                
                # 3. Sur Windows, scanner spécifique (si demandé)
                if IS_WINDOWS and extended_freebox_detection:
                    logger.debug("Démarrage du scan Windows spécifique...")
                    try:
                        # Doubler la durée pour le scanner Windows qui peut être plus lent
                        windows_devices = windows_scanner.scan(duration * 1.5, filter_name)
                        
                        # Traiter les appareils Windows
                        for device in windows_devices:
                            device_id = device["id"]
                            device["source_id"] = device_id
                            device["detected_by"] = device.get("detected_by", "windows_scanner")
                            
                            if deduplicate_devices:
                                # Vérifier si cet appareil est déjà connu
                                if device_id in all_devices:
                                    all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                                elif self._find_matching_device(device, all_devices):
                                    # Appareil similaire trouvé, fusion
                                    match_id = self._find_matching_device(device, all_devices)
                                    all_devices[match_id] = merge_device_info(all_devices[match_id], device)
                                else:
                                    # Nouvel appareil
                                    all_devices[device_id] = device
                            else:
                                # Sans déduplication
                                all_devices[device_id] = device
                        
                    except Exception as e:
                        logger.error(f"Erreur lors du scan Windows: {str(e)}")
                    
                # 4. Sur Windows, scanner avancé pour détecter plus d'appareils (TV, Freebox, etc.)
                if IS_WINDOWS and extended_freebox_detection:
                    logger.debug("Démarrage du scan Windows avancé...")
                    try:
                        # Ce scanner a besoin de plus de temps pour détecter les appareils spéciaux
                        windows_advanced_devices = windows_advanced_scanner.scan(duration * 2, filter_name)
                        
                        # Traiter les appareils Windows avancés
                        for device in windows_advanced_devices:
                            device_id = device["id"]
                            device["source_id"] = device_id
                            device["detected_by"] = device.get("detected_by", "windows_advanced_scanner")
                            
                            if deduplicate_devices:
                                # Vérifier si cet appareil est déjà connu
                                if device_id in all_devices:
                                    all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                                elif self._find_matching_device(device, all_devices):
                                    # Appareil similaire trouvé, fusion
                                    match_id = self._find_matching_device(device, all_devices)
                                    all_devices[match_id] = merge_device_info(all_devices[match_id], device)
                                else:
                                    # Nouvel appareil
                                    all_devices[device_id] = device
                            else:
                                # Sans déduplication
                                all_devices[device_id] = device
                        
                    except Exception as e:
                        logger.error(f"Erreur lors du scan Windows avancé: {str(e)}")
            
            # Déduplication finale basée sur les critères avancés si demandé
            if deduplicate_devices:
                all_devices = self._advanced_deduplication(all_devices)
            
            logger.debug(f"Scan total terminé. {len(all_devices)} appareil(s) unique(s) trouvé(s)")
            
            # Convertir les dictionnaires en modèles BluetoothDevice
            return [BluetoothDevice(**device) for device in all_devices.values()]
            
        except Exception as e:
            logger.error(f"Erreur lors du scan Bluetooth: {str(e)}", exc_info=True)
            raise BluetoothScanError(f"Erreur lors du scan Bluetooth: {str(e)}")

    async def _windows_advanced_scan_task(self, duration: float, filter_name: Optional[str]) -> List[Dict[str, Any]]:
        """Tâche asynchrone pour le scan Windows avancé"""
        try:
            logger.debug("Démarrage du scan Windows avancé asynchrone...")
            devices = await windows_advanced_scanner.scan_async(duration, filter_name)
            
            # Marquer les appareils avec leur source
            for device in devices:
                device["source_id"] = device["id"]
                if "detected_by" not in device:
                    device["detected_by"] = "windows_advanced_scanner"
                
            logger.debug(f"Scan Windows avancé terminé. {len(devices)} appareil(s) trouvé(s)")
            return devices
        except Exception as e:
            logger.error(f"Erreur lors du scan Windows avancé: {str(e)}")
            return []

    async def _ble_scan_task(self, duration: float, filter_name: Optional[str], connect_for_details: bool) -> List[Dict[str, Any]]:
        """Tâche asynchrone pour le scan BLE"""
        try:
            logger.debug("Démarrage du scan BLE asynchrone...")
            devices = await ble_scanner.scan(duration, filter_name, connect_for_details)
            
            # Marquer les appareils avec leur source
            for device in devices:
                device["source_id"] = device["id"]
                device["detected_by"] = "ble_scanner"
                
            logger.debug(f"Scan BLE terminé. {len(devices)} appareil(s) trouvé(s)")
            return devices
        except Exception as e:
            logger.error(f"Erreur lors du scan BLE: {str(e)}")
            return []

    async def _classic_scan_task(self, duration: float, filter_name: Optional[str]) -> List[Dict[str, Any]]:
        """Tâche asynchrone pour le scan Bluetooth classique"""
        try:
            logger.debug("Démarrage du scan Bluetooth classique asynchrone...")
            # Comme classic_scanner.scan est synchrone, l'exécuter dans un thread séparé
            devices = await asyncio.to_thread(classic_scanner.scan, duration * 1.5, filter_name)
            
            # Marquer les appareils avec leur source
            for device in devices:
                device["source_id"] = device["id"]
                device["detected_by"] = "classic_scanner"
                
            logger.debug(f"Scan Bluetooth classique terminé. {len(devices)} appareil(s) trouvé(s)")
            return devices
        except Exception as e:
            logger.error(f"Erreur lors du scan Bluetooth classique: {str(e)}")
            return []

    async def _windows_scan_task(self, duration: float, filter_name: Optional[str]) -> List[Dict[str, Any]]:
        """Tâche asynchrone pour le scan Windows spécifique"""
        try:
            logger.debug("Démarrage du scan Windows asynchrone...")
            # Comme windows_scanner.scan est synchrone, l'exécuter dans un thread séparé
            devices = await asyncio.to_thread(windows_scanner.scan, duration * 2, filter_name)
            
            # Marquer les appareils avec leur source
            for device in devices:
                device["source_id"] = device["id"]
                if "detected_by" not in device:
                    device["detected_by"] = "windows_scanner"
                
            logger.debug(f"Scan Windows terminé. {len(devices)} appareil(s) trouvé(s)")
            return devices
        except Exception as e:
            logger.error(f"Erreur lors du scan Windows: {str(e)}")
            return []

    def _find_matching_device(self, device: Dict[str, Any], device_dict: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Recherche un appareil correspondant dans le dictionnaire d'appareils
        
        Args:
            device: L'appareil à rechercher
            device_dict: Dictionnaire des appareils existants
            
        Returns:
            ID de l'appareil correspondant, ou None si aucune correspondance
        """
        for existing_id, existing_device in device_dict.items():
            if self._device_matches(existing_device, device):
                return existing_id
        return None

    def _advanced_deduplication(self, devices: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Effectue une déduplication avancée en fusionnant les appareils similaires
        
        Args:
            devices: Dictionnaire des appareils à dédupliquer
            
        Returns:
            Dictionnaire des appareils dédupliqués
        """
        result = {}
        processed_ids = set()
        
        # Trier les appareils par RSSI (du plus fort au plus faible)
        sorted_devices = sorted(
            devices.items(), 
            key=lambda x: x[1].get("rssi", -100) if x[1].get("rssi") is not None else -100,
            reverse=True
        )
        
        # Parcourir les appareils triés
        for device_id, device in sorted_devices:
            if device_id in processed_ids:
                continue
                
            # Ajouter l'appareil au résultat
            result[device_id] = device
            processed_ids.add(device_id)
            
            # Rechercher des appareils similaires
            for other_id, other_device in devices.items():
                if other_id in processed_ids:
                    continue
                    
                if self._device_matches(device, other_device):
                    # Fusionner l'appareil similaire avec l'appareil actuel
                    result[device_id] = merge_device_info(result[device_id], other_device)
                    processed_ids.add(other_id)
        
        return result

    def _normalize_device_id(self, address: str) -> str:
        """
        Normalise une adresse d'appareil pour l'utiliser comme clé de déduplication
        
        Args:
            address: L'adresse de l'appareil
            
        Returns:
            L'adresse normalisée pour la déduplication
        """
        if not address:
            return ""
        
        # Pour les adresses MAC, les normaliser au format standard
        if self._is_mac_address(address):
            return normalize_mac_address(address)
        
        # Pour les autres formats, retourner simplement l'adresse
        return address

    def _is_mac_address(self, address: str) -> bool:
        """
        Vérifie si une chaîne ressemble à une adresse MAC
        
        Args:
            address: La chaîne à vérifier
            
        Returns:
            True si la chaîne ressemble à une adresse MAC, False sinon
        """
        if not address:
            return False
        
        # Supprimer tous les séparateurs courants et vérifier s'il reste des caractères hexadécimaux
        clean = address.upper().replace(':', '').replace('-', '').replace('.', '')
        # Vérifier si la chaîne contient au moins 12 caractères hexadécimaux
        return len(clean) >= 12 and all(c in '0123456789ABCDEF' for c in clean[:12])

    def _names_match(self, name1: str, name2: str, threshold: float = 0.7) -> bool:
        """
        Vérifie si deux noms d'appareils semblent correspondre
        en utilisant une comparaison basique
        
        Args:
            name1: Premier nom
            name2: Deuxième nom
            threshold: Seuil de correspondance (0.0-1.0)
            
        Returns:
            True si les noms semblent correspondre, False sinon
        """
        if not name1 or not name2:
            return False
        
        # Normalisation des noms (minuscules)
        name1 = name1.lower()
        name2 = name2.lower()
        
        # Correspondance parfaite
        if name1 == name2:
            return True
        
        # L'un contient l'autre
        if name1 in name2 or name2 in name1:
            return True
        
        # Calcul d'une distance simple (caractères communs)
        common_chars = set(name1) & set(name2)
        if len(common_chars) / max(len(set(name1)), len(set(name2))) >= threshold:
            return True
        
        # Vérifier les sous-chaînes communes
        for length in range(3, min(len(name1), len(name2)) + 1):
            for i in range(len(name1) - length + 1):
                if name1[i:i+length] in name2:
                    return True
        
        return False
    
    def _device_matches(self, device1: Dict[str, Any], device2: Dict[str, Any]) -> bool:
        """
        Détermine si deux appareils correspondent probablement au même appareil physique
        
        Args:
            device1: Premier appareil
            device2: Deuxième appareil
            
        Returns:
            True si les appareils semblent correspondre, False sinon
        """
        # Cas 1: Adresses MAC identiques (normalisées)
        if self._is_mac_address(device1.get("address", "")) and self._is_mac_address(device2.get("address", "")):
            norm_addr1 = self._normalize_device_id(device1["address"])
            norm_addr2 = self._normalize_device_id(device2["address"])
            if norm_addr1 and norm_addr2 and norm_addr1 == norm_addr2:
                return True
        
        # Cas 2: Mêmes noms significatifs
        if (device1.get("name") and device2.get("name") and 
            device1["name"] != "Unknown" and device2["name"] != "Unknown" and
            self._names_match(device1["name"], device2["name"])):
            return True
        
        # Cas 2.5: Noms décodés qui correspondent
        if device1.get("name") and device2.get("name"):
            from app.utils.bluetooth_utils import decode_ascii_name
            decoded_name1 = decode_ascii_name(device1["name"])
            decoded_name2 = decode_ascii_name(device2["name"])
            
            if decoded_name1 != device1["name"] or decoded_name2 != device2["name"]:
                if decoded_name1 and decoded_name2 and self._names_match(decoded_name1, decoded_name2):
                    return True
        
        # Cas 3: Nom convivial identique et non générique
        if (device1.get("friendly_name") and device2.get("friendly_name") and
            "Device" not in device1["friendly_name"] and "Device" not in device2["friendly_name"] and
            self._names_match(device1["friendly_name"], device2["friendly_name"])):
            return True
            
        # Cas 4: Source ID contenu dans merged_from
        if device1.get("source_id") and device2.get("merged_from") and device1["source_id"] in device2["merged_from"]:
            return True
        if device2.get("source_id") and device1.get("merged_from") and device2["source_id"] in device1["merged_from"]:
            return True
        
        # Cas 5: Services UUID identiques (pour les UUID significatifs)
        significant_uuids = [
            # Services communs bien connus
            "0000180f-0000-1000-8000-00805f9b34fb",  # Battery Service
            "00001800-0000-1000-8000-00805f9b34fb",  # Generic Access
            "00001801-0000-1000-8000-00805f9b34fb",  # Generic Attribute
            "0000180a-0000-1000-8000-00805f9b34fb",  # Device Information
            "0000180d-0000-1000-8000-00805f9b34fb",  # Heart Rate
            "00001803-0000-1000-8000-00805f9b34fb",  # Link Loss
            "00001805-0000-1000-8000-00805f9b34fb",  # Current Time
            "00001812-0000-1000-8000-00805f9b34fb",  # Human Interface Device
            "00001813-0000-1000-8000-00805f9b34fb",  # Scan Parameters
            "00001819-0000-1000-8000-00805f9b34fb",  # Location and Navigation
        ]
        
        if device1.get("service_uuids") and device2.get("service_uuids"):
            # Vérifier si au moins un UUID significatif est présent dans les deux appareils
            common_uuids = set(device1["service_uuids"]) & set(device2["service_uuids"])
            for uuid in significant_uuids:
                if uuid in common_uuids:
                    return True
        
        # Cas 6: Identifiants de fabricant identiques (si disponibles)
        if device1.get("manufacturer_data") and device2.get("manufacturer_data"):
            # Si les deux appareils ont des données de fabricant, vérifier s'ils partagent au moins un ID
            common_manufacturers = set(device1["manufacturer_data"].keys()) & set(device2["manufacturer_data"].keys())
            if common_manufacturers:
                return True
        
        return False

# Création d'une instance du service pour pouvoir l'importer facilement
bluetooth_service = BluetoothService()
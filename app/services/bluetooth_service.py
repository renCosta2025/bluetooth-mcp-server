"""
Service principal pour la gestion des opérations Bluetooth.
Ce service orchestre l'utilisation des scanners BLE, classique et Windows spécifique.
"""
import logging
import platform
from typing import List, Optional, Dict, Any

from app.models.bluetooth import BluetoothDevice
from app.services.ble_scanner import ble_scanner
from app.services.classic_scanner import classic_scanner, CLASSIC_BT_AVAILABLE
from app.utils.bluetooth_utils import merge_device_info

# Import conditionnel du scanner Windows
IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
    from app.services.windows_scanner import windows_scanner

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
                          extended_freebox_detection: bool = True) -> List[BluetoothDevice]:
        """
        Effectue un scan des appareils Bluetooth à proximité (BLE et classique)
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            connect_for_details: Si True, se connecte à chaque appareil pour plus d'informations
            include_classic: Si True, inclut les appareils Bluetooth classiques
            extended_freebox_detection: Si True, utilise des méthodes spéciales pour détecter la Freebox
            
        Returns:
            Liste des appareils Bluetooth détectés
            
        Raises:
            BluetoothScanError: En cas d'erreur pendant le scan
        """
        try:
            logger.debug(f"Démarrage du scan Bluetooth complet (durée: {duration}s, filtre: {filter_name}, "
                         f"connexion détaillée: {connect_for_details}, Bluetooth classique: {include_classic}, "
                         f"détection Freebox: {extended_freebox_detection})")
            
            # Dictionnaire pour stocker tous les appareils découverts (par adresse MAC)
            all_devices = {}
            
            # Partie 1: Scan BLE avec Bleak
            logger.debug("Démarrage du scan BLE...")
            ble_devices = await ble_scanner.scan(duration, filter_name, connect_for_details)
            
            # Ajouter les appareils BLE au dictionnaire
            for device in ble_devices:
                all_devices[device["address"]] = device
            
            # Partie 2: Scan Bluetooth classique (si demandé et disponible)
            if include_classic and CLASSIC_BT_AVAILABLE:
                logger.debug("Démarrage du scan Bluetooth classique...")
                classic_devices = classic_scanner.scan(duration, filter_name)
                
                # Fusionner les appareils classiques avec les appareils BLE existants ou les ajouter
                for device in classic_devices:
                    if device["address"] in all_devices:
                        # L'appareil existe déjà, fusion des informations
                        all_devices[device["address"]] = merge_device_info(
                            all_devices[device["address"]], 
                            device
                        )
                    else:
                        # Nouvel appareil, ajout simple
                        all_devices[device["address"]] = device
            elif include_classic and not CLASSIC_BT_AVAILABLE and not IS_WINDOWS:
                logger.warning("Le module Bluetooth classique n'est pas disponible. "
                               "Installation recommandée: pip install pybluez2")
            
            # Partie 3: Sur Windows, utiliser le scanner Windows spécifique
            if IS_WINDOWS and extended_freebox_detection:
                logger.debug("Démarrage du scan Windows spécifique (optimisé pour Freebox)...")
                try:
                    # Doubler la durée pour le scanner Windows qui peut être plus lent
                    windows_devices = windows_scanner.scan(duration * 2, filter_name)
                    
                    # Ajouter les appareils Windows au dictionnaire
                    for device in windows_devices:
                        if device["address"] in all_devices:
                            # Fusion avec un appareil existant
                            all_devices[device["address"]] = merge_device_info(
                                all_devices[device["address"]], 
                                device
                            )
                        else:
                            # Nouvel appareil
                            all_devices[device["address"]] = device
                            
                    logger.debug(f"Scan Windows terminé. {len(windows_devices)} appareil(s) trouvé(s)")
                except Exception as e:
                    logger.error(f"Erreur lors du scan Windows: {str(e)}")
            
            logger.debug(f"Scan total terminé. {len(all_devices)} appareil(s) unique(s) trouvé(s)")
            
            # Convertir les dictionnaires en modèles BluetoothDevice
            return [BluetoothDevice(**device) for device in all_devices.values()]
            
        except Exception as e:
            logger.error(f"Erreur lors du scan Bluetooth: {str(e)}", exc_info=True)
            raise BluetoothScanError(f"Erreur lors du scan Bluetooth: {str(e)}")

# Création d'une instance du service pour pouvoir l'importer facilement
bluetooth_service = BluetoothService()
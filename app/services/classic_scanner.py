"""
Module spécialisé pour le scan Bluetooth classique.
Sur Windows, cette fonctionnalité est limitée et fournit un message d'information.
"""
import logging
import platform
import asyncio
from typing import Dict, List, Optional, Any

from app.utils.bluetooth_utils import get_friendly_device_name
from app.data.mac_prefixes import get_device_info

# Configurer le logging
logger = logging.getLogger(__name__)

# Vérifier si nous sommes sur Windows
IS_WINDOWS = platform.system() == "Windows"

# Flag indiquant si le scan Bluetooth classique est disponible
CLASSIC_BT_AVAILABLE = False

# Message explicatif pour les utilisateurs Windows
WINDOWS_BT_MESSAGE = """
Le scan Bluetooth classique n'est pas disponible sur Windows via cette implémentation.
Cela est dû aux limitations des bibliothèques Python pour Bluetooth sur Windows.
Le scan BLE reste pleinement fonctionnel et peut détecter la plupart des appareils modernes.

Pour certains appareils comme la Freebox, nous utilisons une base de données 
de préfixes MAC pour les identifier même sans le scan classique.
"""

# Initialisation conditionnelle pour les systèmes non-Windows
if not IS_WINDOWS:
    try:
        import bluetooth as bt_classic
        CLASSIC_BT_AVAILABLE = True
        logger.info("Bluetooth classique activé - bibliothèque trouvée")
    except ImportError:
        logger.warning("Bluetooth classique non disponible - bibliothèque non trouvée")
else:
    logger.info(WINDOWS_BT_MESSAGE)

class ClassicBTScanner:
    """Classe spécialisée dans le scan d'appareils Bluetooth classiques"""
    
    def scan(self, duration: float = 10.0, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Effectue un scan Bluetooth classique.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils Bluetooth classiques détectés
        """
        if IS_WINDOWS:
            logger.info("Scan Bluetooth classique ignoré sur Windows")
            return []
            
        if not CLASSIC_BT_AVAILABLE:
            logger.warning("PyBluez n'est pas disponible pour le scan Bluetooth classique.")
            return []
        
        try:
            logger.debug("Recherche d'appareils Bluetooth classiques...")
            nearby_devices = bt_classic.discover_devices(
                duration=int(duration),
                lookup_names=True,
                lookup_class=True,
                device_id=-1
            )
            
            logger.debug(f"Scan Bluetooth classique terminé. {len(nearby_devices)} appareil(s) trouvé(s)")
            
            devices = []
            for addr, name, device_class in nearby_devices:
                if name is None or name == "":
                    name = "Unknown"
                
                # Appliquer le filtre si nécessaire
                if filter_name is None or (filter_name.lower() in name.lower()):
                    # Obtenir les informations de l'appareil à partir de l'adresse MAC
                    device_info = get_device_info(addr)
                    company_name = device_info.get("company", None) if device_info else None
                    
                    # Obtenir un nom convivial
                    friendly_name = device_info.get("friendly_name", "") if device_info else get_friendly_device_name(
                        name, 
                        addr
                    )
                    
                    # Décodage de la classe de l'appareil
                    major_class, minor_class, service_classes = self._decode_device_class(device_class)
                    
                    # Construire l'objet device
                    bluetooth_device = {
                        "id": str(addr),
                        "address": addr,
                        "name": name,
                        "rssi": None,  # Non disponible en Bluetooth classique
                        "manufacturer_data": {},
                        "service_uuids": [],
                        "service_data": {},
                        "tx_power": None,
                        "appearance": None,
                        "company_name": company_name,
                        "is_connectable": True,  # Les appareils Bluetooth classiques sont généralement connectables
                        "device_type": "Classic",
                        "friendly_name": friendly_name,
                        "device_class": device_class,
                        "major_device_class": major_class,
                        "minor_device_class": minor_class,
                        "service_classes": service_classes,
                        "detected_by": "classic_scanner"
                    }
                    
                    devices.append(bluetooth_device)
            
            logger.debug(f"Après filtrage Bluetooth classique: {len(devices)} appareil(s) retourné(s)")
            return devices
        except Exception as e:
            logger.error(f"Erreur lors du scan Bluetooth classique: {str(e)}", exc_info=True)
            return []
    
    async def scan_async(self, duration: float = 10.0, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Version asynchrone du scan Bluetooth classique.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils Bluetooth classiques détectés
        """
        # Exécuter le scan synchrone dans un thread pour ne pas bloquer la boucle d'événements
        return await asyncio.to_thread(self.scan, duration, filter_name)
            
    def _decode_device_class(self, device_class: int) -> tuple:
        """
        Décode la classe de l'appareil Bluetooth en composants lisibles.
        
        Args:
            device_class: La classe de l'appareil (int)
            
        Returns:
            Un tuple (major_class, minor_class, service_classes)
        """
        # Masques pour les bits de classe (selon la spécification Bluetooth)
        major_class_mask = 0x1F00
        minor_class_mask = 0xFF
        service_class_mask = 0xFFE000
        
        # Extraction des classes
        major_class_value = (device_class & major_class_mask) >> 8
        minor_class_value = device_class & minor_class_mask
        service_classes_value = (device_class & service_class_mask) >> 13
        
        # Dictionnaire des classes majeures
        major_classes = {
            0: "Miscellaneous",
            1: "Computer",
            2: "Phone",
            3: "LAN/Network Access Point",
            4: "Audio/Video",
            5: "Peripheral",
            6: "Imaging",
            7: "Wearable",
            8: "Toy",
            9: "Health",
            31: "Uncategorized"
        }
        
        # Dictionnaire des classes de service
        service_classes_dict = {
            0: "Limited Discoverable Mode",
            1: "Reserved",
            2: "Reserved",
            3: "Positioning",
            4: "Networking",
            5: "Rendering",
            6: "Capturing",
            7: "Object Transfer",
            8: "Audio",
            9: "Telephony",
            10: "Information"
        }
        
        # Récupérer les noms des classes
        major_class = major_classes.get(major_class_value, f"Unknown ({major_class_value})")
        minor_class = f"0x{minor_class_value:02x}"  # Format hexadécimal
        
        # Récupérer les classes de service actives
        service_classes = []
        for bit in range(11):  # 11 bits pour les classes de service
            if service_classes_value & (1 << bit):
                service_classes.append(service_classes_dict.get(bit, f"Unknown ({bit})"))
        
        return major_class, minor_class, service_classes

# Instance singleton pour faciliter l'importation
classic_scanner = ClassicBTScanner()
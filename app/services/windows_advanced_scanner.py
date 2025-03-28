"""
Module spécialisé pour la détection avancée d'appareils Bluetooth sous Windows
en utilisant diverses méthodes spécifiques à Windows.
"""
import logging
import platform
import subprocess
import re
import asyncio
import winreg
import time
import os
from typing import Dict, List, Optional, Any

from app.utils.bluetooth_utils import get_friendly_device_name, normalize_mac_address
from app.data.mac_prefixes import get_device_info

# Configurer le logging
logger = logging.getLogger(__name__)

# Vérifier que nous sommes sur Windows
if platform.system() != "Windows":
    logger.warning("Ce module est spécifique à Windows et ne fonctionnera pas sur d'autres systèmes")

class WindowsAdvancedScanner:
    """Scanner avancé pour Windows utilisant plusieurs méthodes de détection"""
    
    def scan(self, duration: float = 10.0, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Effectue un scan avancé des appareils Bluetooth sous Windows en utilisant
        multiples méthodes et sources de données.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils détectés
        """
        # Dictionnaire pour stocker tous les appareils détectés (par ID unique)
        all_devices = {}
        
        try:
            logger.debug("Démarrage du scan Windows avancé...")
            
            # Méthode 1: Appareils appairés via le registre
            paired_devices = self._scan_paired_devices()
            for device in paired_devices:
                if filter_name is None or (device.get("name") and filter_name.lower() in device.get("name").lower()):
                    all_devices[device["id"]] = device
            
            # Méthode 2: Appareils du gestionnaire de périphériques
            dm_devices = self._scan_device_manager_devices(duration)
            for device in dm_devices:
                if filter_name is None or (device.get("name") and filter_name.lower() in device.get("name").lower()):
                    all_devices[device["id"]] = device
            
            # Méthode 3: Appareils Bluetooth via PowerShell
            ps_devices = self._scan_powershell_devices(duration)
            for device in ps_devices:
                if filter_name is None or (device.get("name") and filter_name.lower() in device.get("name").lower()):
                    all_devices[device["id"]] = device
                    
            # Méthode 4: Appareils radios Bluetooth
            radio_devices = self._scan_bluetooth_radios(duration)
            for device in radio_devices:
                if filter_name is None or (device.get("name") and filter_name.lower() in device.get("name").lower()):
                    all_devices[device["id"]] = device
            
            # Méthode 5: Appareils détectables
            discoverable_devices = self._scan_discoverable_devices(duration)
            for device in discoverable_devices:
                if filter_name is None or (device.get("name") and filter_name.lower() in device.get("name").lower()):
                    all_devices[device["id"]] = device
            
            # Méthode 6: Appareils récemment connectés
            recent_devices = self._scan_recent_devices()
            for device in recent_devices:
                if filter_name is None or (device.get("name") and filter_name.lower() in device.get("name").lower()):
                    all_devices[device["id"]] = device
                    
            logger.debug(f"Scan Windows avancé terminé. {len(all_devices)} appareil(s) unique(s) trouvé(s)")
            
            return list(all_devices.values())
            
        except Exception as e:
            logger.error(f"Erreur lors du scan Windows avancé: {str(e)}", exc_info=True)
            return []
    
    async def scan_async(self, duration: float = 10.0, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Version asynchrone du scan Windows avancé.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils détectés
        """
        return await asyncio.to_thread(self.scan, duration, filter_name)
    
    def _scan_paired_devices(self) -> List[Dict[str, Any]]:
        """
        Récupère la liste des appareils Bluetooth déjà appairés à Windows
        via le registre Windows.
        
        Returns:
            Liste de dictionnaires contenant les informations des appareils appairés
        """
        devices = []
        
        try:
            logger.debug("Récupération des appareils appairés via le registre...")
            
            # Chemins du registre à explorer
            registry_paths = [
                r"SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices",
                r"SYSTEM\CurrentControlSet\Services\BTH\Parameters\Devices",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Bluetooth\Devices"
            ]
            
            for registry_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                        # Nombre de sous-clés
                        num_subkeys = winreg.QueryInfoKey(key)[0]
                        
                        for i in range(num_subkeys):
                            try:
                                device_addr = winreg.EnumKey(key, i)
                                
                                # Accéder à la sous-clé de l'appareil
                                with winreg.OpenKey(key, device_addr) as device_key:
                                    # Tenter de récupérer diverses propriétés
                                    name = None
                                    for prop_name in ["Name", "FriendlyName", "DeviceName", "DeviceDesc"]:
                                        try:
                                            name, _ = winreg.QueryValueEx(device_key, prop_name)
                                            if name:
                                                break
                                        except:
                                            pass
                                    
                                    if not name:
                                        name = "Unknown Paired Device"
                                    
                                    # Essayer de formater l'adresse MAC
                                    formatted_addr = device_addr
                                    if len(device_addr) >= 12:
                                        formatted_addr = ':'.join([device_addr[i:i+2] for i in range(0, min(12, len(device_addr)), 2)]).upper()
                                    
                                    device_id = f"WIN-PAIRED-{device_addr}"
                                    
                                    # Récupérer d'autres propriétés si disponibles
                                    device_class = None
                                    try:
                                        class_val, _ = winreg.QueryValueEx(device_key, "Class")
                                        device_class = f"0x{class_val:08X}"
                                    except:
                                        pass
                                    
                                    # Vérifier si c'est un appareil connu (TV, box, etc.)
                                    is_special_device = "TV" in name or "Freebox" in name or "Box" in name or "Bouygtel" in name
                                    
                                    # Si c'est un appareil spécial ou s'il a un nom, l'ajouter
                                    if name != "Unknown Paired Device" or is_special_device:
                                        devices.append({
                                            "id": device_id,
                                            "address": formatted_addr,
                                            "name": name,
                                            "rssi": -60,  # Valeur par défaut
                                            "manufacturer_data": {},
                                            "service_uuids": [],
                                            "service_data": {},
                                            "device_type": "Windows-Paired",
                                            "company_name": "Unknown (Windows Paired)",
                                            "friendly_name": name,
                                            "detected_by": "windows_registry_paired",
                                            "raw_info": f"Registry Path: {registry_path}, Device Class: {device_class}"
                                        })
                            except Exception as e:
                                logger.debug(f"Erreur lors de la lecture d'un appareil appairé: {str(e)}")
                except Exception as e:
                    logger.debug(f"Erreur lors de l'accès au chemin de registre {registry_path}: {str(e)}")
            
            logger.debug(f"Récupération terminée: {len(devices)} appareil(s) appairé(s) trouvé(s)")
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des appareils appairés: {str(e)}")
        
        return devices
    
    def _scan_device_manager_devices(self, duration: float) -> List[Dict[str, Any]]:
        """
        Récupère les appareils Bluetooth depuis le Gestionnaire de périphériques
        via PowerShell.
        
        Args:
            duration: Durée maximale pour l'exécution de la commande
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils du Device Manager
        """
        devices = []
        
        try:
            logger.debug("Récupération des appareils depuis le Gestionnaire de périphériques...")
            
            # Commande PowerShell pour récupérer les appareils du Device Manager
            powershell_cmd = [
                'powershell',
                '-NoProfile',
                '-Command',
                """
                $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
                try {
                    # Obtenir tous les appareils Bluetooth, Media et autres catégories pertinentes
                    Get-PnpDevice -Class Bluetooth,Media,AudioEndpoint,HIDClass | Where-Object { $_.Status -eq 'OK' } | ForEach-Object {
                        Write-Output ("DM-DEVICE: " + $_.FriendlyName + " | ID: " + $_.DeviceID + " | Class: " + $_.Class)
                    }
                    
                    # Recherche spécifique des TV, Freebox et autres appareils spéciaux
                    Get-PnpDevice | Where-Object { 
                        ($_.FriendlyName -like "*TV*" -or 
                         $_.FriendlyName -like "*Freebox*" -or 
                         $_.FriendlyName -like "*Box*" -or
                         $_.FriendlyName -like "*Bouygtel*") -and 
                        $_.Status -eq 'OK' 
                    } | ForEach-Object {
                        Write-Output ("SPECIAL-DEVICE: " + $_.FriendlyName + " | ID: " + $_.DeviceID + " | Class: " + $_.Class)
                    }
                } catch {
                    Write-Output "Error: $_"
                }
                """
            ]
            
            # Exécuter la commande
            result = subprocess.run(
                powershell_cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration,
                encoding='utf-8'
            )
            
            # Analyser les résultats
            device_pattern = r'(DM|SPECIAL)-DEVICE: (.*) \| ID: (.*) \| Class: (.*)'
            
            for line in result.stdout.splitlines():
                match = re.match(device_pattern, line)
                if match:
                    device_type = match.group(1).strip()
                    name = match.group(2).strip()
                    device_id = match.group(3).strip()
                    device_class = match.group(4).strip()
                    
                    # Créer un ID unique pour l'appareil
                    clean_device_id = device_id.replace('&', '-').replace('\\', '-')
                    unique_id = f"WIN-DM-{clean_device_id}"

                    
                    # Essayer d'extraire une adresse MAC si présente
                    mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', device_id)
                    address = mac_match.group(0) if mac_match else unique_id[:17]
                    
                    # Définir la priorité (mettre en avant les appareils spéciaux)
                    rssi = -40 if device_type == "SPECIAL" else -60
                    
                    # Vérifier le type d'appareil pour enrichir les données
                    device_info = None
                    if "TV" in name:
                        device_info = {"company": "TV Manufacturer", "device_type": "TV", "friendly_name": name}
                    elif "Freebox" in name:
                        device_info = {"company": "Freebox SA", "device_type": "Freebox", "friendly_name": name}
                    elif "Box" in name:
                        device_info = {"company": "ISP Provider", "device_type": "Set-top Box", "friendly_name": name}
                    elif "Bouygtel" in name:
                        device_info = {"company": "Bouygues Telecom", "device_type": "Set-top Box", "friendly_name": name}
                    
                    # Créer l'objet appareil
                    device = {
                        "id": unique_id,
                        "address": address,
                        "name": name,
                        "rssi": rssi,
                        "manufacturer_data": {},
                        "service_uuids": [],
                        "service_data": {},
                        "device_type": f"Windows-{device_class}",
                        "company_name": device_info["company"] if device_info else "Unknown (Windows)",
                        "friendly_name": name,
                        "detected_by": "windows_device_manager",
                        "raw_info": f"Class: {device_class}, ID: {device_id}, Type: {device_type}",
                        "is_special_device": device_type == "SPECIAL"
                    }
                    
                    devices.append(device)
            
            logger.debug(f"Récupération terminée: {len(devices)} appareil(s) trouvé(s) dans le Gestionnaire de périphériques")
            
        except Exception as e:
            logger.error(f"Erreur lors du scan du Gestionnaire de périphériques: {str(e)}")
        
        return devices
    
    def _scan_powershell_devices(self, duration: float) -> List[Dict[str, Any]]:
        """
        Récupère les appareils Bluetooth via PowerShell en utilisant les API
        spécifiques à Windows.
        
        Args:
            duration: Durée maximale pour l'exécution de la commande
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils
        """
        devices = []
        
        try:
            logger.debug("Récupération des appareils via PowerShell...")
            
            # Commande PowerShell plus avancée pour accéder aux appareils Bluetooth
            powershell_cmd = [
                'powershell',
                '-NoProfile',
                '-Command',
                """
                $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
                try {
                    # Essayer de charger les assemblies Windows Runtime
                    Add-Type -AssemblyName System.Runtime.WindowsRuntime
                    
                    # Fonction pour attendre les tâches asynchrones
                    function Await($WinRtTask, $ResultType) {
                        $asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 })[0].MakeGenericMethod($ResultType)
                        $netTask = $asTask.Invoke($null, @($WinRtTask))
                        $netTask.Wait(-1) | Out-Null
                        $netTask.Result
                    }
                    
                    # Charger les namespaces nécessaires
                    [Windows.Devices.Enumeration.DeviceInformation,Windows.Devices.Enumeration,ContentType=WindowsRuntime] | Out-Null
                    
                    # 1. Recherche d'appareils Bluetooth avec des filtres plus larges
                    $selectors = @(
                        # Sélecteur standard Bluetooth
                        [Windows.Devices.Bluetooth.BluetoothDevice]::GetDeviceSelector(),
                        # Sélecteur pour les radios Bluetooth
                        [Windows.Devices.Radios.Radio]::GetRadiosAsync(),
                        # Sélecteur pour les appareils audio
                        [Windows.Devices.Enumeration.DeviceClass]::AudioRender,
                        # Sélecteur pour les appareils vidéo
                        [Windows.Devices.Enumeration.DeviceClass]::VideoDisplay
                    )
                    
                    foreach ($selector in $selectors) {
                        try {
                            $devicesAsync = [Windows.Devices.Enumeration.DeviceInformation]::FindAllAsync($selector)
                            $foundDevices = Await $devicesAsync ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Enumeration.DeviceInformation]])
                            
                            foreach ($device in $foundDevices) {
                                Write-Output ("PS-DEVICE: " + $device.Name + " | ID: " + $device.Id + " | Kind: " + $device.Kind)
                                
                                # Ajouter les propriétés utiles
                                $device.Properties | ForEach-Object {
                                    foreach ($prop in $_.Keys) {
                                        Write-Output ("PROP: " + $prop + " = " + $device.Properties[$prop])
                                    }
                                }
                                Write-Output ("---")
                            }
                        } catch {
                            Write-Output ("Selector Error: $_")
                        }
                    }
                    
                    # 2. Recherche spécifique des TV, Freebox et autres appareils spéciaux
                    try {
                        $specialSelector = "System.Devices.DevObjectType:=5 AND System.Devices.Aep.ProtocolId:=\"{e0cbf06c-cd8b-4647-bb8a-263b43f0f974}\""
                        $specialDevicesAsync = [Windows.Devices.Enumeration.DeviceInformation]::FindAllAsync($specialSelector, $null)
                        $specialDevices = Await $specialDevicesAsync ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Enumeration.DeviceInformation]])
                        
                        foreach ($device in $specialDevices) {
                            Write-Output ("SPECIAL-PS-DEVICE: " + $device.Name + " | ID: " + $device.Id + " | Kind: " + $device.Kind)
                            
                            # Ajouter les propriétés utiles
                            $device.Properties | ForEach-Object {
                                foreach ($prop in $_.Keys) {
                                    Write-Output ("PROP: " + $prop + " = " + $device.Properties[$prop])
                                }
                            }
                            Write-Output ("---")
                        }
                    } catch {
                        Write-Output ("Special Selector Error: $_")
                    }
                    
                } catch {
                    Write-Output "General Error: $_"
                }
                """
            ]
            
            # Exécuter la commande
            result = subprocess.run(
                powershell_cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration,
                encoding='utf-8'
            )
            
            # Analyser les résultats
            device_pattern = r'(PS|SPECIAL-PS)-DEVICE: (.*) \| ID: (.*) \| Kind: (.*)'
            prop_pattern = r'PROP: (.*) = (.*)'
            
            current_device = None
            properties = {}
            
            for line in result.stdout.splitlines():
                device_match = re.match(device_pattern, line)
                if device_match:
                    # Si on avait un appareil en cours, l'ajouter à la liste
                    if current_device:
                        # Enrichir l'appareil avec les propriétés
                        self._enrich_device_with_properties(current_device, properties)
                        devices.append(current_device)
                        properties = {}
                    
                    device_type = device_match.group(1).strip()
                    name = device_match.group(2).strip()
                    device_id = device_match.group(3).strip()
                    device_kind = device_match.group(4).strip()
                    
                    # Ignorer les appareils sans nom
                    if not name or name == "":
                        current_device = None
                        continue
                    
                    # Créer un ID unique pour l'appareil
                    clean_device_id = device_id.replace('#', '-').replace('\\', '-')  # Nettoyage des caractères
                    unique_id = f"WIN-PS-{clean_device_id}"  # Création de l'identifiant

                    
                    # Essayer d'extraire une adresse MAC si présente
                    mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', device_id)
                    address = mac_match.group(0) if mac_match else unique_id[:17]
                    
                    # Définir la priorité (mettre en avant les appareils spéciaux)
                    rssi = -40 if device_type == "SPECIAL-PS" else -60
                    
                    # Créer l'objet appareil
                    current_device = {
                        "id": unique_id,
                        "address": address,
                        "name": name,
                        "rssi": rssi,
                        "manufacturer_data": {},
                        "service_uuids": [],
                        "service_data": {},
                        "device_type": f"Windows-{device_kind}",
                        "company_name": "Unknown (Windows PowerShell)",
                        "friendly_name": name,
                        "detected_by": "windows_powershell",
                        "raw_info": f"Kind: {device_kind}, ID: {device_id}, Type: {device_type}",
                        "is_special_device": device_type == "SPECIAL-PS"
                    }
                
                elif line == "---":
                    # Fin des propriétés pour cet appareil
                    if current_device:
                        # Enrichir l'appareil avec les propriétés
                        self._enrich_device_with_properties(current_device, properties)
                        devices.append(current_device)
                        current_device = None
                        properties = {}
                
                elif current_device:
                    # Collecter les propriétés
                    prop_match = re.match(prop_pattern, line)
                    if prop_match:
                        prop_name = prop_match.group(1).strip()
                        prop_value = prop_match.group(2).strip()
                        properties[prop_name] = prop_value
            
            # Ajouter le dernier appareil si nécessaire
            if current_device:
                # Enrichir l'appareil avec les propriétés
                self._enrich_device_with_properties(current_device, properties)
                devices.append(current_device)
            
            logger.debug(f"Récupération PowerShell terminée: {len(devices)} appareil(s) trouvé(s)")
            
        except Exception as e:
            logger.error(f"Erreur lors du scan PowerShell: {str(e)}")
        
        return devices
    
    def _scan_bluetooth_radios(self, duration: float) -> List[Dict[str, Any]]:
        """
        Détecte les radios Bluetooth disponibles sur le système.
        
        Args:
            duration: Durée maximale pour l'exécution de la commande
            
        Returns:
            Liste de dictionnaires contenant les informations des radios Bluetooth
        """
        devices = []
        
        try:
            logger.debug("Recherche des radios Bluetooth...")
            
            # Commande PowerShell pour récupérer les radios Bluetooth
            powershell_cmd = [
                'powershell',
                '-NoProfile',
                '-Command',
                """
                $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
                try {
                    # Essayer d'utiliser Get-PnpDevice pour les radios
                    Get-PnpDevice -Class Bluetooth,Net | Where-Object { 
                        $_.FriendlyName -like "*Radio*" -or 
                        $_.FriendlyName -like "*Bluetooth*" -or
                        $_.FriendlyName -like "*Wireless*"
                    } | ForEach-Object {
                        Write-Output ("RADIO: " + $_.FriendlyName + " | ID: " + $_.DeviceID + " | Status: " + $_.Status)
                    }
                    
                    # Utiliser Get-NetAdapter pour les adaptateurs Bluetooth
                    Get-NetAdapter | Where-Object { 
                        $_.Name -like "*Bluetooth*" -or 
                        $_.InterfaceDescription -like "*Bluetooth*" 
                    } | ForEach-Object {
                        Write-Output ("BT-ADAPTER: " + $_.Name + " | MAC: " + $_.MacAddress + " | Status: " + $_.Status)
                    }
                } catch {
                    Write-Output "Error: $_"
                }
                """
            ]
            
            # Exécuter la commande
            result = subprocess.run(
                powershell_cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration,
                encoding='utf-8'
            )
            
            # Analyser les résultats
            radio_pattern = r'RADIO: (.*) \| ID: (.*) \| Status: (.*)'
            adapter_pattern = r'BT-ADAPTER: (.*) \| MAC: (.*) \| Status: (.*)'
            
            for line in result.stdout.splitlines():
                radio_match = re.match(radio_pattern, line)
                adapter_match = re.match(adapter_pattern, line)
                
                if radio_match:
                    name = radio_match.group(1).strip()
                    device_id = radio_match.group(2).strip()
                    status = radio_match.group(3).strip()
                    
                    # Créer un ID unique pour l'appareil
                    clean_device_id = device_id.replace('&', '-').replace('\\', '-')  # Nettoyage des caractères
                    unique_id = f"WIN-RADIO-{clean_device_id}"  # Construction de l'identifiant
                    
                    # Vérifier si c'est une radio active
                    if status == "OK":
                        devices.append({
                            "id": unique_id,
                            "address": unique_id[:17],
                            "name": name,
                            "rssi": -30,  # Valeur artificielle forte pour les adaptateurs locaux
                            "manufacturer_data": {},
                            "service_uuids": [],
                            "service_data": {},
                            "device_type": "Windows-Radio",
                            "company_name": "Local Bluetooth Adapter",
                            "friendly_name": name,
                            "detected_by": "windows_radio",
                            "raw_info": f"Status: {status}, ID: {device_id}",
                            "is_local_adapter": True
                        })
                
                elif adapter_match:
                    name = adapter_match.group(1).strip()
                    mac_address = adapter_match.group(2).strip()
                    status = adapter_match.group(3).strip()
                    
                    # Créer un ID unique pour l'appareil
                    unique_id = f"WIN-BT-ADAPTER-{mac_address.replace(':', '-')}"
                    
                    # Vérifier si c'est un adaptateur actif
                    if status == "Up":
                        devices.append({
                            "id": unique_id,
                            "address": mac_address,
                            "name": name,
                            "rssi": -30,  # Valeur artificielle forte pour les adaptateurs locaux
                            "manufacturer_data": {},
                            "service_uuids": [],
                            "service_data": {},
                            "device_type": "Windows-BT-Adapter",
                            "company_name": "Local Bluetooth Adapter",
                            "friendly_name": name,
                            "detected_by": "windows_bt_adapter",
                            "raw_info": f"Status: {status}, MAC: {mac_address}",
                            "is_local_adapter": True
                        })
            
            logger.debug(f"Recherche des radios terminée: {len(devices)} radio(s) trouvée(s)")
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des radios Bluetooth: {str(e)}")
        
        return devices
    
    def _scan_discoverable_devices(self, duration: float) -> List[Dict[str, Any]]:
        """
        Recherche des appareils Bluetooth en mode découvrable à l'aide
        d'une commande PowerShell spécifique.
        
        Args:
            duration: Durée du scan en secondes
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils découvrables
        """
        devices = []
        
        try:
            logger.debug("Recherche des appareils Bluetooth découvrables...")
            
            # Commande PowerShell avancée pour rechercher des appareils découvrables
            powershell_cmd = [
                'powershell',
                '-NoProfile',
                '-ExecutionPolicy', 'Bypass',
                '-Command',
                f"""
                $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
                try {{
                    # Essayer d'utiliser l'interface Windows.Devices.Bluetooth
                    Add-Type -AssemblyName System.Runtime.WindowsRuntime
                    $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }})[0]
                    
                    Function AwaitOperation($WinRtTask, $ResultType) {{
                        $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
                        $netTask = $asTask.Invoke($null, @($WinRtTask))
                        $netTask.Wait(-1) | Out-Null
                        return $netTask.Result
                    }}
                    
                    # Chargement des classes nécessaires
                    [Windows.Devices.Enumeration.DeviceInformation,Windows.Devices.Enumeration,ContentType=WindowsRuntime] | Out-Null
                    [Windows.Devices.Bluetooth.BluetoothDevice,Windows.Devices.Bluetooth,ContentType=WindowsRuntime] | Out-Null
                    [Windows.Devices.Bluetooth.Advertisement.BluetoothLEAdvertisementWatcher,Windows.Devices.Bluetooth.Advertisement,ContentType=WindowsRuntime] | Out-Null
                    
                    # Initialiser et configurer le watcher BLE
                    $bleWatcher = New-Object Windows.Devices.Bluetooth.Advertisement.BluetoothLEAdvertisementWatcher
                    $bleWatcher.ScanningMode = 1  # Active
                    
                    # Liste pour stocker les appareils détectés
                    $devices = @{{}}
                    
                    # Gestionnaire d'événements pour les publicités reçues
                    Register-ObjectEvent -InputObject $bleWatcher -EventName Received -Action {{
                        $device = $Event.SourceArgs.BluetoothAddress
                        $addr = ("{0:X12}" -f $device) -replace '(..)(..)(..)(..)(..)(..)', '$6:$5:$4:$3:$2:$1'
                        $rssi = $Event.SourceArgs.RawSignalStrengthInDBm
                        
                        if (-not $devices.ContainsKey($addr)) {{
                            $devices[$addr] = @{{
                                "Address" = $addr;
                                "RSSI" = $rssi;
                                "Name" = "";
                                "IsConnectable" = $Event.SourceArgs.IsConnectable;
                                "Timestamp" = Get-Date;
                            }}
                            
                            # Essayer d'obtenir plus d'informations sur l'appareil
                            try {{
                                $deviceInfoAsync = [Windows.Devices.Bluetooth.BluetoothLEDevice]::FromBluetoothAddressAsync($device)
                                $deviceInfo = AwaitOperation $deviceInfoAsync ([Windows.Devices.Bluetooth.BluetoothLEDevice])
                                
                                if ($deviceInfo -ne $null) {{
                                    $devices[$addr]["Name"] = $deviceInfo.Name
                                    $devices[$addr]["DeviceInfo"] = $deviceInfo
                                    
                                    # Écrire les informations de l'appareil
                                    $name = if ([string]::IsNullOrEmpty($deviceInfo.Name)) {{ "Unknown" }} else {{ $deviceInfo.Name }}
                                    Write-Output ("DISCOVERABLE: " + $name + " | Address: " + $addr + " | RSSI: " + $rssi)
                                }}
                            }} catch {{
                                # Ignorer les erreurs de connexion
                            }}
                        }}
                    }}
                    
                    # Démarrer le scan
                    $bleWatcher.Start()
                    
                    # Attendre pendant la durée spécifiée
                    Start-Sleep -Seconds {duration}
                    
                    # Arrêter le scan
                    $bleWatcher.Stop()
                    
                    # Afficher tous les appareils découverts
                    foreach ($addr in $devices.Keys) {{
                        $name = if ([string]::IsNullOrEmpty($devices[$addr].Name)) {{ "Unknown" }} else {{ $devices[$addr].Name }}
                        Write-Output ("DISCOVERED: " + $name + " | Address: " + $addr + " | RSSI: " + $devices[$addr].RSSI)
                    }}
                    
                    # Recherche des appareils Bluetooth classiques
                    # Utiliser BluetoothClient si disponible
                    try {{
                        Add-Type -Path "$env:SystemRoot\\System32\\bthprops.cpl" -ErrorAction Stop
                        
                        $discoverer = New-Object -TypeName "Microsoft.Bluetooth.BluetoothClient"
                        $discDevices = $discoverer.DiscoverDevices(30)
                        
                        foreach ($device in $discDevices) {{
                            Write-Output ("BT-CLASSIC: " + $device.DeviceName + " | Address: " + $device.DeviceAddress + " | Authenticated: " + $device.Authenticated)
                        }}
                    }} catch {{
                        Write-Output ("BluetoothClient not available: " + $_)
                    }}
                    
                }} catch {{
                    Write-Output "Error during discovery: $_"
                    Write-Output $_.ScriptStackTrace
                }}
                """
            ]
            
            # Exécuter la commande PowerShell
            result = subprocess.run(
                powershell_cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration + 5,  # Ajouter une marge pour le timeout
                encoding='utf-8'
            )
            
            # Analyser les résultats
            discoverable_pattern = r'(DISCOVERABLE|DISCOVERED): (.*) \| Address: (.*) \| RSSI: (.*)'
            classic_pattern = r'BT-CLASSIC: (.*) \| Address: (.*) \| Authenticated: (.*)'
            
            for line in result.stdout.splitlines():
                discoverable_match = re.match(discoverable_pattern, line)
                classic_match = re.match(classic_pattern, line)
                
                if discoverable_match:
                    device_type = discoverable_match.group(1).strip()
                    name = discoverable_match.group(2).strip()
                    address = discoverable_match.group(3).strip()
                    rssi = int(discoverable_match.group(4).strip())
                    
                    # Créer un ID unique pour l'appareil
                    unique_id = address
                    
                    # Vérifier si c'est un appareil avec un nom
                    if name and name != "Unknown":
                        devices.append({
                            "id": unique_id,
                            "address": address,
                            "name": name,
                            "rssi": rssi,
                            "manufacturer_data": {},
                            "service_uuids": [],
                            "service_data": {},
                            "device_type": "Windows-Discoverable-BLE",
                            "company_name": "Unknown (Discoverable)",
                            "friendly_name": name,
                            "detected_by": "windows_discoverable",
                            "raw_info": f"Type: {device_type}, RSSI: {rssi}",
                            "is_discoverable": True
                        })
                
                elif classic_match:
                    name = classic_match.group(1).strip()
                    address = classic_match.group(2).strip()
                    authenticated = classic_match.group(3).strip().lower() == "true"
                    
                    # Créer un ID unique pour l'appareil
                    unique_id = address
                    
                    # Ajouter l'appareil à la liste
                    devices.append({
                        "id": unique_id,
                        "address": address,
                        "name": name,
                        "rssi": -60,  # Valeur par défaut pour les appareils classiques
                        "manufacturer_data": {},
                        "service_uuids": [],
                        "service_data": {},
                        "device_type": "Windows-Classic",
                        "company_name": "Unknown (Classic)",
                        "friendly_name": name,
                        "detected_by": "windows_classic",
                        "raw_info": f"Authenticated: {authenticated}",
                        "is_authenticated": authenticated
                    })
            
            logger.debug(f"Recherche des appareils découvrables terminée: {len(devices)} appareil(s) trouvé(s)")
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des appareils découvrables: {str(e)}")
        
        return devices
    
    def _scan_recent_devices(self) -> List[Dict[str, Any]]:
        """
        Recherche des appareils Bluetooth récemment connectés via
        le registre Windows.
        
        Returns:
            Liste de dictionnaires contenant les informations des appareils récents
        """
        devices = []
        
        try:
            logger.debug("Recherche des appareils récemment connectés...")
            
            # Liste des chemins du registre à vérifier
            registry_paths = [
                # Appareils audio
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render",
                # Appareils Bluetooth spécifiques
                r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Bluetooth\Devices",
                # Historique des connexions
                r"HKEY_CURRENT_USER\Software\Microsoft\WindowsNT\CurrentVersion\EMDMgmt"
            ]
            
            # Exécuter une commande PowerShell pour lire le registre
            powershell_cmd = [
                'powershell',
                '-NoProfile',
                '-Command',
                """
                $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
                
                function Get-RegistryDevices {
                    param (
                        [string]$Path
                    )
                    
                    try {
                        # Vérifier si le chemin existe
                        if (Test-Path $Path) {
                            # Obtenir toutes les sous-clés
                            $subkeys = Get-ChildItem -Path $Path -ErrorAction SilentlyContinue
                            
                            foreach ($key in $subkeys) {
                                try {
                                    # Lire les valeurs de la clé
                                    $values = Get-ItemProperty -Path $key.PSPath -ErrorAction SilentlyContinue
                                    
                                    # Vérifier s'il y a des propriétés intéressantes
                                    $deviceName = $null
                                    $deviceAddr = $null
                                    
                                    if ($values.FriendlyName) {
                                        $deviceName = $values.FriendlyName
                                    } elseif ($values.DeviceName) {
                                        $deviceName = $values.DeviceName
                                    } elseif ($values.Name) {
                                        $deviceName = $values.Name
                                    } elseif ($values.DisplayName) {
                                        $deviceName = $values.DisplayName
                                    }
                                    
                                    # Essayer de trouver une adresse
                                    if ($values.BluetoothAddress) {
                                        $deviceAddr = $values.BluetoothAddress
                                    } elseif ($values.Address) {
                                        $deviceAddr = $values.Address
                                    } elseif ($key.Name -match "([0-9A-Fa-f]{12})$") {
                                        $deviceAddr = $matches[1]
                                    }
                                    
                                    # Si nous avons un nom, ajouter l'appareil
                                    if ($deviceName -and ($deviceName -like "*TV*" -or $deviceName -like "*Freebox*" -or $deviceName -like "*Box*" -or $deviceName -like "*Bouygtel*")) {
                                        $keyPath = $key.Name -replace "HKEY_LOCAL_MACHINE", "HKLM:" -replace "HKEY_CURRENT_USER", "HKCU:"
                                        Write-Output ("RECENT: " + $deviceName + " | ID: " + ($deviceAddr -or $key.PSChildName) + " | Path: " + $keyPath)
                                    }
                                    
                                    # Récursivement chercher dans les sous-clés
                                    Get-RegistryDevices -Path $key.PSPath
                                } catch {
                                    # Ignorer les erreurs pour cette clé
                                }
                            }
                        }
                    } catch {
                        Write-Output "Error scanning path $Path : $_"
                    }
                }
                
                # Parcourir tous les chemins du registre
                foreach ($path in @('HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices\\Audio\\Render', 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Bluetooth\\Devices', 'HKCU:\\Software\\Microsoft\\WindowsNT\\CurrentVersion\\EMDMgmt')) {
                    Get-RegistryDevices -Path $path
                }
                """
            ]
            
            # Exécuter la commande
            result = subprocess.run(
                powershell_cmd, 
                capture_output=True, 
                text=True, 
                timeout=10,  # Timeout plus court
                encoding='utf-8'
            )
            
            # Analyser les résultats
            recent_pattern = r'RECENT: (.*) \| ID: (.*) \| Path: (.*)'
            
            for line in result.stdout.splitlines():
                match = re.match(recent_pattern, line)
                if match:
                    name = match.group(1).strip()
                    device_id = match.group(2).strip()
                    reg_path = match.group(3).strip()
                    
                    # Essayer de formater l'ID en adresse MAC si possible
                    address = device_id
                    if len(device_id) >= 12 and all(c in "0123456789ABCDEFabcdef" for c in device_id):
                        address = ':'.join([device_id[i:i+2] for i in range(0, min(12, len(device_id)), 2)]).upper()
                    
                    # Créer un ID unique pour l'appareil
                    unique_id = f"WIN-RECENT-{device_id}"
                    
                    # Ajouter l'appareil à la liste
                    devices.append({
                        "id": unique_id,
                        "address": address,
                        "name": name,
                        "rssi": -50,  # Valeur artificielle forte pour les appareils récents
                        "manufacturer_data": {},
                        "service_uuids": [],
                        "service_data": {},
                        "device_type": "Windows-Recent",
                        "company_name": "Unknown (Recent)",
                        "friendly_name": name,
                        "detected_by": "windows_recent",
                        "raw_info": f"Path: {reg_path}",
                        "is_recent": True
                    })
            
            logger.debug(f"Recherche des appareils récents terminée: {len(devices)} appareil(s) trouvé(s)")
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des appareils récents: {str(e)}")
        
        return devices
    
    def _enrich_device_with_properties(self, device: Dict[str, Any], properties: Dict[str, str]) -> None:
        """
        Enrichit un appareil avec des propriétés supplémentaires.
        
        Args:
            device: L'appareil à enrichir
            properties: Les propriétés à ajouter
        """
        # Propriétés intéressantes à rechercher
        if "System.Devices.ModelName" in properties:
            device["model"] = properties["System.Devices.ModelName"]
        
        if "System.Devices.Manufacturer" in properties:
            device["company_name"] = properties["System.Devices.Manufacturer"]
        
        if "System.Devices.Category" in properties:
            device["category"] = properties["System.Devices.Category"]
        
        # Détecter les appareils spéciaux
        if any(keyword in str(properties) for keyword in ["TV", "Freebox", "Box", "Bouygtel", "Téléviseur"]):
            device["is_special_device"] = True
            
            # Déterminer le type d'appareil spécial
            if "TV" in str(properties) or "Téléviseur" in str(properties):
                device["device_type"] = "TV"
                if "Samsung" in str(properties):
                    device["company_name"] = "Samsung Electronics Co. Ltd."
            elif "Freebox" in str(properties):
                device["device_type"] = "Freebox"
                device["company_name"] = "Freebox SA"
            elif "Bouygtel" in str(properties):
                device["device_type"] = "Bouygtel"
                device["company_name"] = "Bouygues Telecom"

# Instance singleton pour faciliter l'importation
windows_advanced_scanner = WindowsAdvancedScanner()
"""
Module spécialisé pour le scan Bluetooth sur Windows en utilisant les API natives.
Ceci est une alternative au scanner classique qui nécessite pybluez2.
"""
import logging
import platform
import subprocess
import re
import time
import os
import asyncio
from typing import Dict, List, Optional, Any
from app.utils.bluetooth_utils import decode_ascii_name

from app.utils.bluetooth_utils import get_friendly_device_name
from app.data.mac_prefixes import get_device_info

# Configurer le logging
logger = logging.getLogger(__name__)

# Vérifier si nous sommes sur Windows
IS_WINDOWS = platform.system() == "Windows"

class WindowsBTScanner:
    """Scanner Bluetooth spécifique à Windows utilisant les commandes système"""
    
    def scan(self, duration: float = 10.0, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Effectue un scan Bluetooth sur Windows via les commandes système.
        
        Args:
            duration: Durée du scan en secondes (utilisé comme timeout)
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils Bluetooth
        """
        if not IS_WINDOWS:
            logger.warning("Ce scanner est spécifique à Windows et ne fonctionnera pas sur d'autres systèmes")
            return []
        
        # Dictionnaire pour stocker tous les appareils détectés (par adresse MAC ou ID unique)
        all_devices = {}
        
        try:
            # Exécution parallèle des différentes méthodes de scan Windows
            # pour accélérer le processus
            all_devices = self._run_parallel_scans(duration, filter_name)
            
            # Convertir le dictionnaire en liste
            devices = list(all_devices.values())
            logger.debug(f"Scan Windows terminé. {len(devices)} appareil(s) unique(s) trouvé(s)")
            return devices
            
        except Exception as e:
            logger.error(f"Erreur lors du scan Bluetooth Windows: {str(e)}", exc_info=True)
            return []
    
    async def scan_async(self, duration: float = 10.0, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Version asynchrone du scan Windows.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Liste de dictionnaires contenant les informations des appareils Bluetooth
        """
        # Exécuter le scan synchrone dans un thread pour ne pas bloquer la boucle d'événements
        return await asyncio.to_thread(self.scan, duration, filter_name)
    
    def _run_parallel_scans(self, duration: float, filter_name: Optional[str]) -> Dict[str, Dict[str, Any]]:
        """
        Exécute les différentes méthodes de scan Windows en parallèle.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Dictionnaire des appareils détectés
        """
        import concurrent.futures
        
        all_devices = {}
        
        # Liste des méthodes de scan à exécuter en parallèle
        scan_methods = [
            self._scan_pnp_devices,
            self._scan_bluetooth_adapter,
            self._scan_wmi_devices,
            self._scan_netsh_devices,
            self._scan_registry_devices
        ]
        
        # Exécuter les méthodes de scan en parallèle
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(scan_methods)) as executor:
            # Démarrer toutes les tâches
            futures = {executor.submit(method, duration / len(scan_methods), filter_name): method.__name__ 
                       for method in scan_methods}
            
            # Collecter les résultats au fur et à mesure qu'ils sont disponibles
            for future in concurrent.futures.as_completed(futures):
                method_name = futures[future]
                try:
                    devices = future.result()
                    logger.debug(f"Méthode {method_name} terminée. {len(devices)} appareil(s) trouvé(s)")
                    
                    # Fusionner les résultats
                    for device_id, device in devices.items():
                        if device_id in all_devices:
                            # Fusionner les informations
                            all_devices[device_id].update(device)
                        else:
                            # Nouvel appareil
                            all_devices[device_id] = device
                except Exception as e:
                    logger.error(f"Erreur lors de l'exécution de {method_name}: {str(e)}")
        
        return all_devices
    
    def _scan_pnp_devices(self, duration: float, filter_name: Optional[str]) -> Dict[str, Dict[str, Any]]:
        """
        Scan des appareils PnP via PowerShell Get-PnpDevice.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Dictionnaire des appareils détectés
        """
        devices = {}
        
        # Commande PowerShell avec sortie encodée en UTF-8
        powershell_cmd = [
            'powershell',
            '-NoProfile',
            '-Command',
            """
            $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
            # Essayons d'abord via Get-PnpDevice
            try {
                $btDevices = Get-PnpDevice -Class Bluetooth | Where-Object { $_.Status -eq 'OK' }
                foreach ($dev in $btDevices) {
                    Write-Output ("Device: " + $dev.FriendlyName + " | ID: " + $dev.DeviceID + " | Status: " + $dev.Status)
                }
            } catch {
                Write-Output "Error: $_"
            }
            """
        ]
        
        # Exécuter la commande avec un timeout et encodage UTF-8
        try:
            ps_result = subprocess.run(
                powershell_cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration,
                encoding='utf-8'
            )
            
            logger.debug(f"Résultat Get-PnpDevice: {len(ps_result.stdout.splitlines())} lignes")
            
            # Analyse des résultats
            device_pattern = r'Device: (.*) \| ID: (.*) \| Status: (.*)'
            
            for line in ps_result.stdout.splitlines():
                match = re.match(device_pattern, line)
                if match:
                    name = match.group(1).strip()
                    device_id = match.group(2).strip()
                    status = match.group(3).strip()
                    
                    # Appliquer le filtre si nécessaire
                    if filter_name is not None and filter_name.lower() not in name.lower():
                        continue
                    
                    if "freebox" in name.lower() or "free" in name.lower():
                        logger.info(f"Freebox trouvée via Get-PnpDevice: {name}")
                        
                    # Créer un ID unique pour l'appareil
                    device_id_clean = device_id.replace('&', '-').replace('\\', '-')
                    unique_id = f"WIN-PNP-{device_id_clean}"
                    
                    # Ajouter l'appareil au dictionnaire
                    devices[unique_id] = {
                        "id": unique_id,
                        "address": unique_id[:17] if len(unique_id) > 17 else unique_id,
                        "name": name,
                        "rssi": -60,  # Valeur fictive
                        "manufacturer_data": {},
                        "service_uuids": [],
                        "service_data": {},
                        "tx_power": None,
                        "appearance": None,
                        "company_name": "Unknown (Windows)",
                        "device_type": "Windows-PnP",
                        "friendly_name": name,
                        "detected_by": "windows_pnp",
                        "raw_info": f"ID: {device_id}, Status: {status}"
                    }
        except (subprocess.SubprocessError, UnicodeDecodeError) as e:
            logger.error(f"Erreur avec Get-PnpDevice: {str(e)}")
        
        return devices
    
    def _scan_bluetooth_adapter(self, duration: float, filter_name: Optional[str]) -> Dict[str, Dict[str, Any]]:
        """
        Scan via PowerShell BluetoothAdapter.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Dictionnaire des appareils détectés
        """
        devices = {}
        
        bt_adapter_cmd = [
            'powershell',
            '-NoProfile',
            '-Command',
            """
            $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
            try {
                Add-Type -AssemblyName System.Runtime.WindowsRuntime
                $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
                
                Function Await($WinRtTask, $ResultType) {
                    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
                    $netTask = $asTask.Invoke($null, @($WinRtTask))
                    $netTask.Wait()
                    $netTask.Result
                }
                
                [Windows.Devices.Enumeration.DeviceInformation,Windows.Devices.Enumeration,ContentType=WindowsRuntime] | Out-Null
                [Windows.Devices.Bluetooth.BluetoothAdapter,Windows.Devices.Bluetooth,ContentType=WindowsRuntime] | Out-Null
                
                $bluetooth = [Windows.Devices.Bluetooth.BluetoothAdapter]::GetDefaultAsync()
                $adapter = Await $bluetooth ([Windows.Devices.Bluetooth.BluetoothAdapter])
                
                if ($adapter) {
                    Write-Output "Bluetooth Adapter Info:"
                    Write-Output "--------------------"
                    Write-Output ("Name: " + $adapter.Name)
                    Write-Output ("ID: " + $adapter.BluetoothAddress)
                    Write-Output ("Status: " + $adapter.ConnectionStatus)
                    
                    # Get paired devices
                    $devices = [Windows.Devices.Enumeration.DeviceInformation]::FindAllAsync([Windows.Devices.Bluetooth.BluetoothDevice]::GetDeviceSelector())
                    $btDevices = Await $devices ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Enumeration.DeviceInformation]])
                    
                    Write-Output ""
                    Write-Output ("Found " + $btDevices.Count + " Bluetooth devices:")
                    Write-Output "--------------------"
                    
                    foreach ($device in $btDevices) {
                        Write-Output ("BT-DEVICE: " + $device.Name + " | ID: " + $device.Id + " | Status: " + $device.Pairing.CanPair)
                    }
                } else {
                    Write-Output "No Bluetooth adapter found"
                }
            } catch {
                Write-Output "Error: $_"
            }
            """
        ]
        
        try:
            bt_result = subprocess.run(
                bt_adapter_cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration,
                encoding='utf-8'
            )
            
            # Analyse des résultats
            bt_device_pattern = r'BT-DEVICE: (.*) \| ID: (.*) \| Status: (.*)'
            device_count = 0
            
            for line in bt_result.stdout.splitlines():
                match = re.match(bt_device_pattern, line)
                if match:
                    device_count += 1
                    name = match.group(1).strip()
                    device_id = match.group(2).strip()
                    status = match.group(3).strip()
                    
                    # Appliquer le filtre si nécessaire
                    if filter_name is not None and filter_name.lower() not in name.lower():
                        continue
                    
                    if "freebox" in name.lower() or "free" in name.lower():
                        logger.info(f"Freebox trouvée via BluetoothAdapter: {name}")
                        
                    # Créer un ID unique pour l'appareil
                    device_id_clean = device_id.replace('#', '-')
                    device_id_clean = device_id_clean[-17:] if len(device_id_clean) > 17 else device_id_clean
                    unique_id = f"WIN-BT-{device_id_clean}"
                    
                    # Extraire l'adresse MAC potentielle du device_id
                    mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', device_id)
                    address = mac_match.group(0) if mac_match else unique_id[:17]
                    
                    # Ajouter l'appareil au dictionnaire
                    devices[unique_id] = {
                        "id": unique_id,
                        "address": address,
                        "name": name,
                        "rssi": -55,  # Valeur fictive
                        "manufacturer_data": {},
                        "service_uuids": [],
                        "service_data": {},
                        "tx_power": None,
                        "appearance": None,
                        "company_name": "Unknown (Windows)",
                        "device_type": "Windows-BT",
                        "friendly_name": name,
                        "detected_by": "windows_bluetooth_adapter",
                        "raw_info": f"ID: {device_id}, Status: {status}"
                    }
            
            logger.info(f"Trouvé {device_count} périphériques via BluetoothAdapter")
        except (subprocess.SubprocessError, UnicodeDecodeError) as e:
            logger.error(f"Erreur avec BluetoothAdapter: {str(e)}")
        
        return devices
    
    def _scan_wmi_devices(self, duration: float, filter_name: Optional[str]) -> Dict[str, Dict[str, Any]]:
        """
        Scan via WMI.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Dictionnaire des appareils détectés
        """
        devices = {}
        
        wmi_cmd = [
            'powershell',
            '-NoProfile',
            '-Command',
            """
            $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
            try {
                $wmiDevices = Get-WmiObject -Query "SELECT * FROM Win32_PnPEntity WHERE PNPClass = 'Bluetooth'" | Select-Object Name, DeviceID, Status, Description
                
                if ($wmiDevices) {
                    foreach ($device in $wmiDevices) {
                        Write-Output ("WMI-BT: " + $device.Name + " | ID: " + $device.DeviceID + " | Status: " + $device.Status)
                    }
                } else {
                    Write-Output "No WMI Bluetooth devices found"
                }
            } catch {
                Write-Output "Error: $_"
            }
            """
        ]
        
        try:
            wmi_result = subprocess.run(
                wmi_cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration,
                encoding='utf-8'
            )
            
            # Analyse des résultats
            wmi_device_pattern = r'WMI-BT: (.*) \| ID: (.*) \| Status: (.*)'
            
            for line in wmi_result.stdout.splitlines():
                match = re.match(wmi_device_pattern, line)
                if match:
                    name = match.group(1).strip()
                    device_id = match.group(2).strip()
                    status = match.group(3).strip()
                    
                    # Appliquer le filtre si nécessaire
                    if filter_name is not None and filter_name.lower() not in name.lower():
                        continue
                    
                    if "freebox" in name.lower() or "free" in name.lower():
                        logger.info(f"Freebox trouvée via WMI: {name}")
                        
                    # Créer un ID unique pour l'appareil
                    device_id_clean = device_id.replace('&', '-').replace('\\', '-')
                    unique_id = f"WIN-WMI-{device_id_clean}"
                    
                    # Ajouter l'appareil au dictionnaire s'il n'existe pas déjà
                    devices[unique_id] = {
                        "id": unique_id,
                        "address": unique_id[:17] if len(unique_id) > 17 else unique_id,
                        "name": name,
                        "rssi": -65,  # Valeur fictive
                        "manufacturer_data": {},
                        "service_uuids": [],
                        "service_data": {},
                        "tx_power": None,
                        "appearance": None,
                        "company_name": "Unknown (Windows)",
                        "device_type": "Windows-WMI",
                        "friendly_name": name,
                        "detected_by": "windows_wmi",
                        "raw_info": f"ID: {device_id}, Status: {status}"
                    }
        except (subprocess.SubprocessError, UnicodeDecodeError) as e:
            logger.error(f"Erreur avec WMI: {str(e)}")
        
        return devices
    
    def _scan_netsh_devices(self, duration: float, filter_name: Optional[str]) -> Dict[str, Dict[str, Any]]:
        """
        Scan via netsh.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Dictionnaire des appareils détectés
        """
        devices = {}
        
        netsh_cmd = [
            'netsh',
            'bluetooth',
            'show',
            'devices'
        ]
        
        try:
            netsh_result = subprocess.run(
                netsh_cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration,
                encoding='utf-8'
            )
            
            # Analyse des résultats
            # Exemple de sortie: 
            # Device 1
            #     Device Name: DEV-1234
            #     Bluetooth Address: xx:xx:xx:xx:xx:xx 
            device_block_pattern = r'Device \d+\s+Device Name: (.*)\s+Bluetooth Address: ([0-9a-fA-F:]{17})'
            
            for match in re.finditer(device_block_pattern, netsh_result.stdout, re.DOTALL):
                name = match.group(1).strip()
                address = match.group(2).strip()
                
                # Appliquer le filtre si nécessaire
                if filter_name is not None and filter_name.lower() not in name.lower():
                    continue
                
                if "freebox" in name.lower() or "free" in name.lower():
                    logger.info(f"Freebox trouvée via netsh: {name}")
                
                # Créer un ID unique pour l'appareil
                unique_id = f"WIN-NETSH-{address}"
                
                # Ajouter l'appareil au dictionnaire s'il n'existe pas déjà
                devices[unique_id] = {
                    "id": address,
                    "address": address,
                    "name": name,
                    "rssi": -55,  # Valeur fictive
                    "manufacturer_data": {},
                    "service_uuids": [],
                    "service_data": {},
                    "tx_power": None,
                    "appearance": None,
                    "company_name": "Unknown (Windows)",
                    "device_type": "Windows-NETSH",
                    "friendly_name": name,
                    "detected_by": "windows_netsh",
                    "raw_info": f"Netsh Device: {name}"
                }
        except subprocess.SubprocessError as e:
            logger.error(f"Erreur avec netsh: {str(e)}")
        
        return devices
    
    def _scan_registry_devices(self, duration: float, filter_name: Optional[str]) -> Dict[str, Dict[str, Any]]:
        """
        Recherche spécifique dans le registre Windows.
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Dictionnaire des appareils détectés
        """
        devices = {}
        
        registry_cmd = [
            'powershell',
            '-NoProfile',
            '-Command',
            """
            $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
            try {
                # Rechercher des clés de registre contenant des appareils Bluetooth
                $regKeys = @(
                    "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Devices",
                    "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\BTH\\Parameters\\Devices",
                    "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Bluetooth\\Devices"
                )
                
                foreach ($regKey in $regKeys) {
                    if (Test-Path $regKey) {
                        $devices = Get-ChildItem $regKey -ErrorAction SilentlyContinue
                        foreach ($device in $devices) {
                            $props = Get-ItemProperty -Path $device.PSPath -ErrorAction SilentlyContinue
                            $name = ""
                            
                            # Essayer différentes propriétés qui pourraient contenir un nom
                            if ($props.Name) { $name = $props.Name }
                            elseif ($props.FriendlyName) { $name = $props.FriendlyName }
                            elseif ($props.DeviceName) { $name = $props.DeviceName }
                            elseif ($props.DeviceDesc) { $name = $props.DeviceDesc }
                            
                            # Si le nom contient "free" ou "freebox", c'est potentiellement une Freebox
                            if ($name -match "free" -or $name -match "freebox") {
                                Write-Output ("FREEBOX-REG: " + $name + " | ID: " + $device.PSChildName)
                            }
                            # Sinon, afficher quand même tous les appareils Bluetooth
                            elseif ($name) {
                                Write-Output ("BT-REG: " + $name + " | ID: " + $device.PSChildName)
                            }
                        }
                    }
                }
            } catch {
                Write-Output "Error: $_"
            }
            """
        ]
        
        try:
            registry_result = subprocess.run(
                registry_cmd, 
                capture_output=True, 
                text=True, 
                timeout=duration,
                encoding='utf-8'
            )
            
            # Analyse des résultats
            freebox_reg_pattern = r'FREEBOX-REG: (.*) \| ID: (.*)'
            bt_reg_pattern = r'BT-REG: (.*) \| ID: (.*)'
            
            # D'abord, chercher les entrées Freebox spécifiques
            for line in registry_result.stdout.splitlines():
                match = re.match(freebox_reg_pattern, line)
                if match:
                    name = match.group(1).strip()
                    reg_id = match.group(2).strip()
                    
                    # Appliquer le filtre si nécessaire
                    if filter_name is not None and filter_name.lower() not in name.lower():
                        continue
                    
                    logger.info(f"Freebox trouvée dans le registre: {name}")
                    
                    # Construire une adresse MAC à partir de l'ID du registre si possible
                    address = None
                    if len(reg_id) >= 12:
                        # Convertir l'ID du registre en format MAC
                        address = ':'.join([reg_id[i:i+2] for i in range(0, min(12, len(reg_id)), 2)])
                    else:
                        address = f"FB:FX:{reg_id[-6:] if len(reg_id) >= 6 else '000000'}"
                    
                    # Ajouter la Freebox au dictionnaire
                    devices[f"FREEBOX-REG-{reg_id}"] = {
                        "id": address,
                        "address": address,
                        "name": "Freebox (" + name + ")",
                        "rssi": -50,  # Valeur fictive, priorité plus élevée
                        "manufacturer_data": {},
                        "service_uuids": [],
                        "service_data": {},
                        "tx_power": None,
                        "appearance": None,
                        "company_name": "Freebox SA",
                        "device_type": "Windows-Registry",
                        "friendly_name": "Freebox Player",
                        "detected_by": "windows_registry_specific",
                        "raw_info": f"Registry ID: {reg_id}, Name: {name}"
                    }
            
            # Ensuite, traiter les entrées Bluetooth génériques
            for line in registry_result.stdout.splitlines():
                match = re.match(bt_reg_pattern, line)
                if match:
                    name = match.group(1).strip()
                    reg_id = match.group(2).strip()
                    
                    # Appliquer le filtre si nécessaire
                    if filter_name is not None and filter_name.lower() not in name.lower():
                        continue
                    
                    # Tenter de décoder le nom si c'est une séquence de chiffres séparés par des espaces
                    decoded_name = decode_ascii_name(name)
                    if decoded_name != name:
                        logger.debug(f"Nom décodé de {name} en {decoded_name}")
                        name = decoded_name

                    # Si le nom contient "free" ou "freebox", c'est potentiellement une Freebox
                    if "free" in name.lower() or "freebox" in name.lower():
                        logger.info(f"Freebox trouvée dans le registre (nom générique): {name}")
                        
                        # Construire une adresse MAC
                        address = None
                        if len(reg_id) >= 12:
                            address = ':'.join([reg_id[i:i+2] for i in range(0, min(12, len(reg_id)), 2)])
                        else:
                            address = f"FB:FX:{reg_id[-6:] if len(reg_id) >= 6 else '000000'}"
                        
                        # Ajouter la Freebox au dictionnaire
                        devices[f"FREEBOX-REG-{reg_id}"] = {
                            "id": address,
                            "address": address,
                            "name": "Freebox (" + name + ")",
                            "rssi": -50,
                            "manufacturer_data": {},
                            "service_uuids": [],
                            "service_data": {},
                            "tx_power": None,
                            "appearance": None,
                            "company_name": "Freebox SA",
                            "device_type": "Windows-Registry",
                            "friendly_name": "Freebox Player",
                            "detected_by": "windows_registry_specific",
                            "raw_info": f"Registry ID: {reg_id}, Name: {name}"
                        }
                    else:
                        # Créer un ID unique pour l'appareil
                        unique_id = f"WIN-REG-{reg_id}"
                        
                        # Ajouter l'appareil au dictionnaire s'il n'existe pas déjà
                        devices[unique_id] = {
                            "id": unique_id,
                            "address": unique_id[:17] if len(unique_id) > 17 else unique_id,
                            "name": name,
                            "rssi": -70,  # Valeur fictive
                            "manufacturer_data": {},
                            "service_uuids": [],
                            "service_data": {},
                            "tx_power": None,
                            "appearance": None,
                            "company_name": "Unknown (Windows)",
                            "device_type": "Windows-Registry",
                            "friendly_name": name,  # Utiliser le nom décodé comme nom convivial
                            "detected_by": "windows_registry",
                            "raw_info": f"Registry ID: {reg_id}"
                        }
        except (subprocess.SubprocessError, UnicodeDecodeError) as e:
            logger.error(f"Erreur avec le registre: {str(e)}")
        
        return devices

# Instance singleton pour faciliter l'importation
windows_scanner = WindowsBTScanner()
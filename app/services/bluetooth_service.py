"""
Main service for managing Bluetooth operations.
This service orchestrates the use of BLE, classic, and Windows-specific scanners.
"""
import logging
import platform
import sys
import re
import asyncio
import subprocess
import json
import concurrent.futures
from typing import List, Optional, Dict, Any, Set

from app.models.bluetooth import BluetoothDevice
from app.services.ble_scanner import ble_scanner
from app.services.classic_scanner import classic_scanner, CLASSIC_BT_AVAILABLE
from app.utils.bluetooth_utils import merge_device_info, normalize_mac_address

# Detect platform
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

# Conditional import of platform-specific advanced scanner
if IS_WINDOWS:
    from app.services.windows_advanced_scanner import windows_advanced_scanner as advanced_scanner
elif IS_MACOS:
    from app.services.macos_advanced_scanner import macos_advanced_scanner as advanced_scanner
else:
    advanced_scanner = None

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Thread pool for multithreaded operations
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)


class BluetoothScanError(Exception):
    """Custom exception for Bluetooth scanning errors."""
    pass


class BluetoothService:
    """Service for managing Bluetooth operations (BLE and classic)."""
    
    async def scan_for_devices(
        self,
        duration: float = 5.0,
        filter_name: Optional[str] = None,
        connect_for_details: bool = False,
        include_classic: bool = True,
        extended_freebox_detection: bool = True,
        deduplicate_devices: bool = True,
        parallel_scans: bool = True
    ) -> List[BluetoothDevice]:
        """
        Scan for nearby Bluetooth devices (BLE and classic) 
        with improved duplicate handling and optional parallel execution.
        
        Args:
            duration: Scan duration in seconds.
            filter_name: Optional filter for device names.
            connect_for_details: If True, connect to each device for more details.
            include_classic: If True, include classic Bluetooth devices.
            extended_freebox_detection: If True, use additional methods to detect Freebox devices.
            deduplicate_devices: If True, merge duplicate devices.
            parallel_scans: If True, run BLE/classic scans in parallel.
            
        Returns:
            A list of detected Bluetooth devices.
            
        Raises:
            BluetoothScanError: If any error occurs during scanning.
        """
        try:
            logger.debug(
                f"Starting full Bluetooth scan (duration: {duration}s, filter: {filter_name}, "
                f"detailed connection: {connect_for_details}, classic Bluetooth: {include_classic}, "
                f"Freebox detection: {extended_freebox_detection}, "
                f"deduplication: {deduplicate_devices}, "
                f"parallel scans: {parallel_scans})"
            )
            
            all_devices = {}

            if parallel_scans:
                tasks = [
                    self._ble_scan_task(duration, filter_name, connect_for_details),
                ]

                if include_classic and CLASSIC_BT_AVAILABLE:
                    tasks.append(self._classic_scan_task(duration, filter_name))

                # Cross-platform advanced scanner (macOS or Windows)
                if extended_freebox_detection and advanced_scanner:
                    tasks.append(self._advanced_scan_task(duration, filter_name))

                scan_results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in scan_results:
                    if isinstance(result, Exception):
                        logger.error(f"Scan error: {str(result)}")
                        continue

                    for device in result:
                        device_id = device["id"]
                        if deduplicate_devices and device_id in all_devices:
                            all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                        else:
                            all_devices[device_id] = device

            else:
                # Sequential scans
                ble_devices = await self._ble_scan_task(duration, filter_name, connect_for_details)
                for device in ble_devices:
                    device_id = device["id"]
                    if deduplicate_devices and device_id in all_devices:
                        all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                    else:
                        all_devices[device_id] = device

                if include_classic and CLASSIC_BT_AVAILABLE:
                    classic_devices = await self._classic_scan_task(duration, filter_name)
                    for device in classic_devices:
                        device_id = device["id"]
                        if deduplicate_devices and device_id in all_devices:
                            all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                        else:
                            all_devices[device_id] = device

                if extended_freebox_detection and advanced_scanner:
                    advanced_devices = await self._advanced_scan_task(duration, filter_name)
                    for device in advanced_devices:
                        device_id = device["id"]
                        if deduplicate_devices and device_id in all_devices:
                            all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                        else:
                            all_devices[device_id] = device

                # Windows-only: advanced scan to detect more devices (TV, Freebox, etc.)
                if IS_WINDOWS and extended_freebox_detection:
                    logger.debug("Starting Windows advanced scan...")
                    try:
                        windows_advanced_devices = windows_advanced_scanner.scan(duration * 2, filter_name)
                        for device in windows_advanced_devices:
                            device_id = device["id"]
                            device["source_id"] = device_id
                            device["detected_by"] = device.get("detected_by", "windows_advanced_scanner")
                            
                            if deduplicate_devices:
                                if device_id in all_devices:
                                    all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                                elif self._find_matching_device(device, all_devices):
                                    match_id = self._find_matching_device(device, all_devices)
                                    all_devices[match_id] = merge_device_info(all_devices[match_id], device)
                                else:
                                    all_devices[device_id] = device
                            else:
                                all_devices[device_id] = device
                        
                    except Exception as e:
                        logger.error(f"Windows advanced scan failed: {str(e)}")
            
            # Final deduplication
            if deduplicate_devices:
                all_devices = self._advanced_deduplication(all_devices)
            
            logger.debug(f"Scan finished. {len(all_devices)} unique device(s) found.")
            
            return [BluetoothDevice(**device) for device in all_devices.values()]
            
        except Exception as e:
            logger.error(f"Bluetooth scan failed: {str(e)}", exc_info=True)
            raise BluetoothScanError(f"Bluetooth scan failed: {str(e)}")

    async def _ble_scan_task(self, duration: float, filter_name: Optional[str], connect_for_details: bool) -> List[Dict[str, Any]]:
        """Asynchronous task for BLE scanning."""
        try:
            logger.debug("Starting BLE scan...")
            devices = await ble_scanner.scan(duration, filter_name, connect_for_details)
            
            for device in devices:
                device["source_id"] = device["id"]
                device["detected_by"] = "ble_scanner"
                
            logger.debug(f"BLE scan finished. {len(devices)} device(s) found.")
            return devices
        except Exception as e:
            logger.error(f"BLE scan failed: {str(e)}")
            return []

    async def _classic_scan_task(self, duration: float, filter_name: Optional[str]) -> List[Dict[str, Any]]:
        """Asynchronous task for classic Bluetooth scanning."""
        try:
            logger.debug("Starting classic Bluetooth scan...")
            devices = await asyncio.to_thread(classic_scanner.scan, duration * 1.5, filter_name)
            
            for device in devices:
                device["source_id"] = device["id"]
                device["detected_by"] = "classic_scanner"
                
            logger.debug(f"Classic Bluetooth scan finished. {len(devices)} device(s) found.")
            return devices
        except Exception as e:
            logger.error(f"Classic Bluetooth scan failed: {str(e)}")
            return []

    async def _advanced_scan_task(self, duration, filter_name=None):
        """
        Cross-platform advanced scan using both BLE and classic methods
        to detect devices on macOS or Windows.
        Returns a list of device dictionaries with at least an "id" key.
        """
        all_advanced_devices = []

        try:
            # 1. BLE scan
            ble_devices = await self._ble_scan_task(duration, filter_name, False)
            for device in ble_devices:
                device["detected_by"] = "ble_advanced"
            all_advanced_devices.extend(ble_devices)

            # 2. Classic scan (if available)
            if CLASSIC_BT_AVAILABLE:
                classic_devices = await self._classic_scan_task(duration, filter_name)
                for device in classic_devices:
                    device["detected_by"] = "classic_advanced"
                all_advanced_devices.extend(classic_devices)

            # 3. macOS-specific system_profiler scan
            if sys.platform == "darwin":
                try:
                    result = subprocess.run(
                        ["system_profiler", "-json", "SPBluetoothDataType"],
                        capture_output=True, text=True
                    )
                    data = json.loads(result.stdout)
                    bt_devices = data.get("SPBluetoothDataType", [{}])[0].get("device_title", [])
                    for d in bt_devices:
                        device_id = d.get("device_address")
                        if device_id:
                            all_advanced_devices.append({
                                "id": device_id,
                                "name": d.get("device_name"),
                                "detected_by": "macOS_system_profiler"
                            })
                except Exception as e:
                    logger.error(f"macOS system_profiler scan failed: {str(e)}")

        except Exception as e:
            logger.error(f"Advanced scan failed: {str(e)}")

        return all_advanced_devices

    async def _windows_advanced_scan_task(self, duration: float, filter_name: Optional[str]) -> List[Dict[str, Any]]:
        """Asynchronous task for advanced Windows scanning."""
        try:
            logger.debug("Starting advanced Windows scan...")
            devices = await windows_advanced_scanner.scan_async(duration, filter_name)
            
            for device in devices:
                device["source_id"] = device["id"]
                if "detected_by" not in device:
                    device["detected_by"] = "windows_advanced_scanner"
                
            logger.debug(f"Advanced Windows scan finished. {len(devices)} device(s) found.")
            return devices
        except Exception as e:
            logger.error(f"Advanced Windows scan failed: {str(e)}")
            return []

    def _find_matching_device(self, device: Dict[str, Any], device_dict: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """
        Find a matching device in an existing dictionary of devices.
        
        Args:
            device: Device to look for.
            device_dict: Dictionary of known devices.
            
        Returns:
            Matching device ID, or None if no match is found.
        """
        for existing_id, existing_device in device_dict.items():
            if self._device_matches(existing_device, device):
                return existing_id
        return None

    def _advanced_deduplication(self, devices: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Perform advanced deduplication by merging similar devices.
        
        Args:
            devices: Dictionary of devices to deduplicate.
            
        Returns:
            Deduplicated dictionary of devices.
        """
        result = {}
        processed_ids = set()
        
        sorted_devices = sorted(
            devices.items(), 
            key=lambda x: x[1].get("rssi", -100) if x[1].get("rssi") is not None else -100,
            reverse=True
        )
        
        for device_id, device in sorted_devices:
            if device_id in processed_ids:
                continue
                
            result[device_id] = device
            processed_ids.add(device_id)
            
            for other_id, other_device in devices.items():
                if other_id in processed_ids:
                    continue
                    
                if self._device_matches(device, other_device):
                    result[device_id] = merge_device_info(result[device_id], other_device)
                    processed_ids.add(other_id)
        
        return result

    def _normalize_device_id(self, address: str) -> str:
        """
        Normalise a device address for use as a deduplication key.
        
        Args:
            address: Device address.
            
        Returns:
            Normalised address for deduplication.
        """
        if not address:
            return ""
        
        if self._is_mac_address(address):
            return normalize_mac_address(address)
        
        return address

    def _is_mac_address(self, address: str) -> bool:
        """
        Check if a string looks like a MAC address.
        
        Args:
            address: The string to check.
            
        Returns:
            True if the string resembles a MAC address, otherwise False.
        """
        if not address:
            return False
        
        clean = address.upper().replace(':', '').replace('-', '').replace('.', '')
        return len(clean) >= 12 and all(c in '0123456789ABCDEF' for c in clean[:12])

    def _names_match(self, name1: str, name2: str, threshold: float = 0.7) -> bool:
        """
        Check if two device names likely match using simple comparison.
        
        Args:
            name1: First name.
            name2: Second name.
            threshold: Match threshold (0.0–1.0).
            
        Returns:
            True if names likely match, otherwise False.
        """
        if not name1 or not name2:
            return False
        
        name1 = name1.lower()
        name2 = name2.lower()
        
        if name1 == name2:
            return True
        
        if name1 in name2 or name2 in name1:
            return True
        
        common_chars = set(name1) & set(name2)
        if len(common_chars) / max(len(set(name1)), len(set(name2))) >= threshold:
            return True
        
        for length in range(3, min(len(name1), len(name2)) + 1):
            for i in range(len(name1) - length + 1):
                if name1[i:i+length] in name2:
                    return True
        
        return False
        
    def _device_matches(self, device1: Dict[str, Any], device2: Dict[str, Any]) -> bool:
        """
        Determine if two devices are likely the same physical device.
        
        Args:
            device1: First device.
            device2: Second device.
            
        Returns:
            True if the devices match, otherwise False.
        """
        if self._is_mac_address(device1.get("address", "")) and self._is_mac_address(device2.get("address", "")):
            norm_addr1 = self._normalize_device_id(device1["address"])
            norm_addr2 = self._normalize_device_id(device2["address"])
            if norm_addr1 and norm_addr2 and norm_addr1 == norm_addr2:
                return True
        
        if (device1.get("name") and device2.get("name") and 
            device1["name"] != "Unknown" and device2["name"] != "Unknown" and
            self._names_match(device1["name"], device2["name"])):
            return True
        
        if device1.get("name") and device2.get("name"):
            from app.utils.bluetooth_utils import decode_ascii_name
            decoded_name1 = decode_ascii_name(device1["name"])
            decoded_name2 = decode_ascii_name(device2["name"])
            
            if decoded_name1 != device1["name"] or decoded_name2 != device2["name"]:
                if decoded_name1 and decoded_name2 and self._names_match(decoded_name1, decoded_name2):
                    return True
        
        if (device1.get("friendly_name") and device2.get("friendly_name") and
            "Device" not in device1["friendly_name"] and "Device" not in device2["friendly_name"] and
            self._names_match(device1["friendly_name"], device2["friendly_name"])):
            return True
            
        if device1.get("source_id") and device2.get("merged_from") and device1["source_id"] in device2["merged_from"]:
            return True
        if device2.get("source_id") and device1.get("merged_from") and device2["source_id"] in device1["merged_from"]:
            return True
        
        significant_uuids = [
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
            common_uuids = set(device1["service_uuids"]) & set(device2["service_uuids"])
            for uuid in significant_uuids:
                if uuid in common_uuids:
                    return True
        
        if device1.get("manufacturer_data") and device2.get("manufacturer_data"):
            common_manufacturers = set(device1["manufacturer_data"].keys()) & set(device2["manufacturer_data"].keys())
            if common_manufacturers:
                return True
        
        return False


# Create a service instance for easy import
bluetooth_service = BluetoothService()

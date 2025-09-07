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
                    de

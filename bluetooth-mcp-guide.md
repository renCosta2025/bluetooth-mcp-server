# Bluetooth MCP Server Implementation Guide

<div align="center">

![Implementation Guide](https://img.shields.io/badge/Implementation-Guide-blue?style=for-the-badge)

**Step-by-step guide to implement a Bluetooth MCP Server using Test-Driven Development**

</div>

## 📋 Overview

This guide provides detailed steps for implementing a Model Context Protocol (MCP) server that enables AI assistants like Claude to detect and interact with Bluetooth devices. The implementation uses Python with FastAPI and Bleak for Bluetooth operations, following a Test-Driven Development (TDD) approach.

## 🔧 Prerequisites

Before starting, ensure you have:

- **Python 3.7+** installed
- **Bluetooth adapter** (built-in or external)
- **Administrator/sudo privileges** (needed for Bluetooth operations)
- **Internet connection** (for package installation)
- **Basic knowledge** of Python, FastAPI, and TDD principles

## 🚀 Implementation Roadmap

Our implementation will follow this sequence:

1. Environment setup
2. Test suite development
3. Core models implementation
4. Services implementation
5. API endpoints creation
6. MCP integration
7. Execution and testing

## 1️⃣ Environment Setup

### Create Project Structure

```bash
# Create project directory
mkdir bluetooth-mcp-server
cd bluetooth-mcp-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### Install Dependencies

```bash
# Core dependencies
pip install fastapi uvicorn bleak pydantic python-dotenv

# Testing dependencies
pip install pytest pytest-asyncio httpx

# For Classic Bluetooth support (non-Windows systems)
pip install pybluez2; platform_system != "Windows"

# For MCP integration
pip install model-context-protocol-sdk requests

# Create requirements.txt
pip freeze > requirements.txt
```

### Create Directory Structure

```bash
# Create the basic directory structure
mkdir -p app/{api,core,data,models,services,utils} mcp_sdk tests/{api,models,services,utils}

# Create __init__.py files
touch app/__init__.py app/api/__init__.py app/core/__init__.py app/data/__init__.py \
      app/models/__init__.py app/services/__init__.py app/utils/__init__.py \
      mcp_sdk/__init__.py tests/__init__.py tests/api/__init__.py \
      tests/models/__init__.py tests/services/__init__.py tests/utils/__init__.py
```

## 2️⃣ Test-Driven Development Approach

Following TDD principles, we'll implement each component in this sequence:

1. Write tests for the component
2. Verify that tests fail (red phase)
3. Implement the minimal code to pass tests (green phase)
4. Refactor the code for optimization and clarity (refactor phase)
5. Repeat for each component

## 3️⃣ Core Models Implementation

### Write Model Tests

First, create test files for your models:

```python
# tests/models/test_bluetooth_model.py
import pytest
from pydantic import ValidationError

def test_bluetooth_device_model():
    """Test that the BluetoothDevice model works correctly"""
    # Import the model
    from app.models.bluetooth import BluetoothDevice
    
    # Test with valid data
    device_data = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "Test Device",
        "rssi": -65
    }
    
    device = BluetoothDevice(**device_data)
    assert device.id == "00:11:22:33:44:55"
    assert device.address == "00:11:22:33:44:55"
    assert device.name == "Test Device"
    assert device.rssi == -65
    
    # Test with invalid data (rssi as string)
    invalid_data = {
        "id": "00:11:22:33:44:55",
        "address": "00:11:22:33:44:55",
        "name": "Test Device",
        "rssi": "invalid"
    }
    
    with pytest.raises(ValidationError):
        BluetoothDevice(**invalid_data)

def test_bluetooth_scan_params_model():
    """Test that the BluetoothScanParams model works correctly"""
    # Import the model
    from app.models.bluetooth import BluetoothScanParams
    
    # Test with default values
    params = BluetoothScanParams()
    assert params.duration == 5.0
    assert params.filter_name is None
    
    # Test with custom values
    custom_params = BluetoothScanParams(duration=10.0, filter_name="Test")
    assert custom_params.duration == 10.0
    assert custom_params.filter_name == "Test"
    
    # Test with negative duration (should fail)
    with pytest.raises(ValidationError):
        BluetoothScanParams(duration=-1.0)

def test_scan_response_model():
    """Test that the ScanResponse model works correctly"""
    # Import the models
    from app.models.bluetooth import ScanResponse, BluetoothDevice
    
    # Create some devices for the test
    device1 = BluetoothDevice(
        id="00:11:22:33:44:55",
        address="00:11:22:33:44:55",
        name="Device 1",
        rssi=-65
    )
    
    device2 = BluetoothDevice(
        id="AA:BB:CC:DD:EE:FF",
        address="AA:BB:CC:DD:EE:FF",
        name="Device 2",
        rssi=-80
    )
    
    # Create a scan response
    scan_response = ScanResponse(devices=[device1, device2])
    
    # Verify
    assert len(scan_response.devices) == 2
    assert scan_response.devices[0].name == "Device 1"
    assert scan_response.devices[1].name == "Device 2"
    
    # Test with empty list
    empty_response = ScanResponse(devices=[])
    assert len(empty_response.devices) == 0
```

### Implement Models

After writing the tests, implement the models:

```python
# app/models/bluetooth.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any

class BluetoothDevice(BaseModel):
    """Model representing a detected Bluetooth device with all available information"""
    id: str
    address: str
    name: str
    rssi: Optional[int] = None
    
    # Additional information available during scan
    manufacturer_data: Optional[Dict[int, List[int]]] = None
    service_uuids: Optional[List[str]] = None
    service_data: Optional[Dict[str, List[int]]] = None
    tx_power: Optional[int] = None
    appearance: Optional[int] = None
    
    # Connected information (if requested)
    connected_info: Optional[Dict[str, Any]] = None
    services: Optional[List[Dict[str, Any]]] = None
    characteristics: Optional[List[Dict[str, Any]]] = None
    
    # Inferred information
    device_type: Optional[str] = None  # "BLE", "Classic", "BLE+Classic", etc.
    company_name: Optional[str] = None
    is_connectable: Optional[bool] = None
    device_class: Optional[int] = None  # For Classic Bluetooth
    major_device_class: Optional[str] = None  # For Classic Bluetooth
    minor_device_class: Optional[str] = None  # For Classic Bluetooth
    service_classes: Optional[List[str]] = None  # For Classic Bluetooth
    friendly_name: Optional[str] = None  # More user-friendly name based on other info
    
    # Detection information
    detected_by: Optional[str] = None  # Main detection method
    detection_sources: Optional[List[str]] = None  # All detection sources
    raw_info: Optional[str] = None  # Raw detection information
    detection_note: Optional[str] = None  # Note about detection
    
    # Merge information
    source_id: Optional[str] = None  # Original ID before merging
    merged_from: Optional[List[str]] = None  # List of merged device IDs
    
    # Model configuration
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "00:11:22:33:44:55",
                "address": "00:11:22:33:44:55",
                "name": "Device Name",
                "rssi": -65,
                "manufacturer_data": {76: [0, 22, 1, 1, 11, 0]},
                "service_uuids": ["0000180f-0000-1000-8000-00805f9b34fb"],
                "tx_power": -59,
                "device_type": "BLE",
                "company_name": "Apple, Inc.",
                "friendly_name": "iPhone 13",
                "detection_sources": ["ble_scanner", "windows_registry"],
                "merged_from": ["00:11:22:33:44:55", "WIN-REG-001122334455"]
            }
        }
    }

class BluetoothScanParams(BaseModel):
    """Parameters for Bluetooth device scanning"""
    duration: Optional[float] = 5.0
    filter_name: Optional[str] = None
    connect_for_details: Optional[bool] = False  # If True, attempts to connect for more info
    include_classic: Optional[bool] = True  # If True, includes Classic Bluetooth devices
    extended_freebox_detection: Optional[bool] = True  # If True, enables special Freebox detection
    deduplicate_devices: Optional[bool] = True  # If True, merges duplicate devices
    parallel_scans: Optional[bool] = True  # If True, runs scans in parallel for faster results
    
    @validator('duration')
    def duration_must_be_positive(cls, v):
        """Validation to ensure duration is positive"""
        if v is not None and v <= 0:
            raise ValueError('Duration must be positive')
        return v
        
    @validator('filter_name')
    def filter_name_null_handling(cls, v):
        """Convert special values to None for filter"""
        # Handle cases where filter_name is 'null', 'none', empty string, or 'string'
        if v in [None, 'null', 'none', '', 'string', 'NULL', 'NONE', 'None']:
            return None
        return v

class ScanResponse(BaseModel):
    """Response containing the list of detected Bluetooth devices"""
    devices: List[BluetoothDevice]
```

Also implement session models:

```python
# app/models/session.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any

class SessionResponse(BaseModel):
    """Response for MCP session creation"""
    session: Dict[str, str]
    tools: List[Dict[str, Any]]
    
    @validator('session')
    def session_must_have_id(cls, v):
        """Validation to ensure session has an ID"""
        if 'id' not in v or not v['id']:
            raise ValueError('Session must have an ID')
        return v

# Define available MCP tools
bluetooth_scan_tool = {
    "name": "bluetooth-scan",
    "description": "Scans for nearby Bluetooth devices (BLE and Classic) with extended information",
    "parameters": {
        "type": "object",
        "properties": {
            "duration": {
                "type": "number",
                "description": "Scan duration in seconds (default: 5)"
            },
            "filter_name": {
                "type": "string",
                "description": "Optional name filter for devices (null to see all devices)"
            },
            "connect_for_details": {
                "type": "boolean",
                "description": "If true, attempts to connect to each device for more detailed information (slower)"
            },
            "include_classic": {
                "type": "boolean",
                "description": "If true, includes classic Bluetooth devices in the scan results (recommended)"
            },
            "extended_freebox_detection": {
                "type": "boolean", 
                "description": "If true, uses additional methods to detect Freebox devices (recommended)"
            },
            "deduplicate_devices": {
                "type": "boolean",
                "description": "If true, merges duplicate devices with the same MAC address (recommended)"
            },
            "parallel_scans": {
                "type": "boolean",
                "description": "If true, executes different scan methods in parallel for faster results (default: true)"
            }
        }
    }
}
```

## 4️⃣ Utilities Implementation

Implement utility functions for Bluetooth operations:

```python
# app/utils/bluetooth_utils.py
from typing import Dict, List, Optional, Any

def format_manufacturer_data(mfr_data: Dict) -> Dict[int, List[int]]:
    """
    Convert manufacturer data to a JSON-serializable format.
    
    Args:
        mfr_data: Dictionary of manufacturer data
        
    Returns:
        Formatted dictionary for JSON serialization
    """
    if not mfr_data:
        return {}
    
    result = {}
    for key, value in mfr_data.items():
        # Convert bytes to list of integers
        if isinstance(value, bytes):
            result[key] = list(value)
        else:
            result[key] = list(value)
    return result

def normalize_mac_address(mac_address: str) -> str:
    """
    Normalize a MAC address to standard format.
    
    Args:
        mac_address: MAC address to normalize
        
    Returns:
        Normalized MAC address (XX:XX:XX:XX:XX:XX)
    """
    if not mac_address:
        return ""
        
    # Remove all separators and convert to uppercase
    clean_mac = mac_address.upper().replace(':', '').replace('-', '').replace('.', '')
    
    # Check length
    if len(clean_mac) != 12:
        return mac_address  # Return original if format is incorrect
    
    # Reformat with colons
    return ':'.join([clean_mac[i:i+2] for i in range(0, 12, 2)])

def get_friendly_device_name(device_name: str, mac_address: str, manufacturer_data: Dict = None) -> str:
    """
    Determine a friendly name for the device based on various information sources.
    
    Args:
        device_name: Device name
        mac_address: Device MAC address
        manufacturer_data: Manufacturer data (optional)
        
    Returns:
        Friendly device name
    """
    # Check if device name is already meaningful
    if device_name and device_name != "Unknown":
        return device_name
    
    # Try to get company name from manufacturer data
    company_name = None
    if manufacturer_data:
        # Logic to extract company_name from manufacturer_data
        # (simplified for the example)
        pass
    
    # Build a friendly name
    if company_name:
        return f"{company_name} Device ({mac_address[-8:]})"
    
    # Last resort: just use MAC address
    return f"BT Device {mac_address[-8:]}"

def merge_device_info(device1: Dict[str, Any], device2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge information from two devices into a single device.
    
    Args:
        device1: First device information
        device2: Second device information
        
    Returns:
        Merged device information
    """
    # Basic merging logic
    merged = device1.copy()
    
    # For each field in device2, use it if missing in device1
    for key, value in device2.items():
        if key not in merged or merged[key] is None or merged[key] == "" or merged[key] == [] or merged[key] == {}:
            merged[key] = value
    
    # Special handling for detection sources
    if "detection_sources" not in merged:
        merged["detection_sources"] = []
    
    if device1.get("detected_by") and device1["detected_by"] not in merged["detection_sources"]:
        merged["detection_sources"].append(device1["detected_by"])
    
    if device2.get("detected_by") and device2["detected_by"] not in merged["detection_sources"]:
        merged["detection_sources"].append(device2["detected_by"])
    
    return merged
```

## 5️⃣ Services Implementation

### BLE Scanner Service

```python
# app/services/ble_scanner.py
import logging
import asyncio
from typing import Dict, List, Optional, Any
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from app.utils.bluetooth_utils import format_manufacturer_data, get_friendly_device_name

logger = logging.getLogger(__name__)

class BLEScanner:
    """Class specialized in scanning BLE devices"""
    
    async def scan(self, duration: float = 5.0, filter_name: Optional[str] = None, connect_for_details: bool = False) -> List[Dict[str, Any]]:
        """
        Perform a BLE scan using Bleak.
        
        Args:
            duration: Scan duration in seconds
            filter_name: Optional filter for device names
            connect_for_details: If True, try to connect for more information
            
        Returns:
            List of dictionaries containing BLE device information
        """
        discovered_devices_with_ads = {}
        
        def _device_detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
            """Callback to collect devices and their advertisement data"""
            discovered_devices_with_ads[device.address] = (device, advertisement_data)
            logger.debug(f"Detected (BLE): {device.address}: {device.name}, RSSI: {advertisement_data.rssi}")
        
        # Start scanner with callback
        logger.debug(f"Starting BLE scan with duration of {duration} seconds...")
        
        scanner = BleakScanner(detection_callback=_device_detection_callback)
        await scanner.start()
        await asyncio.sleep(duration)
        await scanner.stop()
        
        logger.debug(f"BLE scan completed. {len(discovered_devices_with_ads)} device(s) found")
        
        devices = []
        
        for address, (device, adv_data) in discovered_devices_with_ads.items():
            device_name = device.name or "Unknown"
            
            # Apply filter if necessary
            if filter_name is None or (filter_name.lower() in device_name.lower()):
                # Build the device object
                bluetooth_device = {
                    "id": str(device.address),
                    "address": device.address,
                    "name": device_name,
                    "rssi": adv_data.rssi,
                    "manufacturer_data": format_manufacturer_data(adv_data.manufacturer_data),
                    "service_uuids": adv_data.service_uuids or [],
                    "service_data": {},  # format_service_data(adv_data.service_data),
                    "tx_power": adv_data.tx_power,
                    "appearance": getattr(adv_data, 'appearance', None),
                    "company_name": None,  # To be filled later
                    "is_connectable": getattr(adv_data, 'connectable', None),
                    "device_type": "BLE",
                    "friendly_name": get_friendly_device_name(device_name, device.address, adv_data.manufacturer_data),
                    "detected_by": "ble_scanner"
                }
                
                # If requested, connect for more details
                if connect_for_details:
                    try:
                        logger.debug(f"Attempting to connect to {device.address}")
                        detailed_info = await self._get_detailed_device_info(device)
                        bluetooth_device["connected_info"] = detailed_info.get("info", {})
                        bluetooth_device["services"] = detailed_info.get("services", [])
                        bluetooth_device["characteristics"] = detailed_info.get("characteristics", [])
                        
                        logger.debug(f"Successfully connected to {device.address}")
                    except Exception as e:
                        logger.warning(f"Unable to connect to {device.address}: {str(e)}")
                
                devices.append(bluetooth_device)
        
        logger.debug(f"After BLE filtering: {len(devices)} device(s) returned")
        return devices
    
    async def _get_detailed_device_info(self, device: BLEDevice) -> Dict[str, Any]:
        """
        Connect to a Bluetooth device and retrieve detailed information.
        
        Args:
            device: BLE device to query
            
        Returns:
            Dictionary containing detailed information about the device
        """
        # Implementation of detailed device information retrieval
        # This would connect to the device and get services, characteristics, etc.
        pass

# Singleton instance for easy importing
ble_scanner = BLEScanner()
```

### Main Bluetooth Service

```python
# app/services/bluetooth_service.py
import logging
import asyncio
from typing import List, Optional

from app.models.bluetooth import BluetoothDevice
from app.services.ble_scanner import ble_scanner
from app.utils.bluetooth_utils import merge_device_info

# Configure logging
logger = logging.getLogger(__name__)

class BluetoothScanError(Exception):
    """Custom exception for Bluetooth scan errors"""
    pass

class BluetoothService:
    """Service to manage Bluetooth operations (BLE and Classic)"""
    
    async def scan_for_devices(self, 
                         duration: float = 5.0, 
                         filter_name: Optional[str] = None, 
                         connect_for_details: bool = False,
                         include_classic: bool = True,
                         extended_freebox_detection: bool = True,
                         deduplicate_devices: bool = True,
                         parallel_scans: bool = True) -> List[BluetoothDevice]:
        """
        Perform a scan for nearby Bluetooth devices (BLE and Classic)
        with enhanced duplicate handling and parallel execution.
        
        Args:
            duration: Scan duration in seconds
            filter_name: Optional filter for device names
            connect_for_details: If True, connect to each device for more information
            include_classic: If True, include Classic Bluetooth devices
            extended_freebox_detection: If True, use special methods to detect Freebox
            deduplicate_devices: If True, merge duplicate devices
            parallel_scans: If True, run different scans in parallel
            
        Returns:
            List of detected Bluetooth devices
            
        Raises:
            BluetoothScanError: On scan error
        """
        try:
            logger.debug(f"Starting full Bluetooth scan (duration: {duration}s, filter: {filter_name})")
            
            # Dictionary to store all discovered devices
            all_devices = {}
            
            if parallel_scans:
                # Parallel execution of different scans
                tasks = []
                
                # 1. BLE scan with Bleak (always active)
                tasks.append(self._ble_scan_task(duration, filter_name, connect_for_details))
                
                # 2. Classic Bluetooth scan (if requested and available)
                # Include other scan types as needed

                # Wait for all scans to complete
                scan_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in scan_results:
                    if isinstance(result, Exception):
                        logger.error(f"A scan method failed: {str(result)}")
                        continue
                    
                    # Merge detected devices
                    for device in result:
                        device_id = device["id"]
                        if deduplicate_devices and device_id in all_devices:
                            all_devices[device_id] = merge_device_info(all_devices[device_id], device)
                        else:
                            all_devices[device_id] = device
            
            else:
                # Sequential execution (older behavior)
                # 1. BLE scan with Bleak
                ble_devices = await ble_scanner.scan(duration, filter_name, connect_for_details)
                
                # Add BLE devices to the dictionary
                for device in ble_devices:
                    device_id = device["id"]
                    device["source_id"] = device_id  # Keep original ID
                    device["detected_by"] = "ble_scanner"
                    
                    all_devices[device_id] = device
                
                # 2. Add other scan types as needed
            
            # Final deduplication if requested
            if deduplicate_devices:
                all_devices = self._advanced_deduplication(all_devices)
            
            logger.debug(f"Total scan completed. {len(all_devices)} unique device(s) found")
            
            # Convert dictionaries to BluetoothDevice models
            return [BluetoothDevice(**device) for device in all_devices.values()]
            
        except Exception as e:
            logger.error(f"Error during Bluetooth scan: {str(e)}", exc_info=True)
            raise BluetoothScanError(f"Error during Bluetooth scan: {str(e)}")
    
    async def _ble_scan_task(self, duration: float, filter_name: Optional[str], connect_for_details: bool) -> List[dict]:
        """Asynchronous task for BLE scanning"""
        try:
            logger.debug("Starting asynchronous BLE scan...")
            devices = await ble_scanner.scan(duration, filter_name, connect_for_details)
            
            # Mark devices with their source
            for device in devices:
                device["source_id"] = device["id"]
                device["detected_by"] = "ble_scanner"
                
            logger.debug(f"BLE scan completed. {len(devices)} device(s) found")
            return devices
        except Exception as e:
            logger.error(f"Error during BLE scan: {str(e)}")
            return []
    
    def _advanced_deduplication(self, devices: dict) -> dict:
        """
        Perform advanced deduplication by merging similar devices
        
        Args:
            devices: Dictionary of devices to deduplicate
            
        Returns:
            Deduplicated dictionary of devices
        """
        # Implementation of advanced deduplication logic
        return devices

# Create a service instance for easy importing
bluetooth_service = BluetoothService()
```

## 6️⃣ API Endpoints Implementation

First, create API router for Bluetooth operations:

```python
# app/api/bluetooth.py
from fastapi import APIRouter, HTTPException
from app.models.bluetooth import BluetoothScanParams, ScanResponse
from app.services.bluetooth_service import bluetooth_service, BluetoothScanError

# Create FastAPI router
router = APIRouter()

@router.post("/mcp/v1/tools/bluetooth-scan", response_model=ScanResponse, 
             description="Scan for nearby Bluetooth devices. "
                         "Use filter_name=null or omit the field to see all devices.")
async def execute_bluetooth_scan(params: BluetoothScanParams):
    """
    Endpoint to execute Bluetooth scan tool.
    Detects BLE and Classic Bluetooth devices nearby.
    
    Args:
        params: Scan parameters
          - duration: Scan duration in seconds (default: 5.0)
          - filter_name: Optional filter for device names (null to see all devices)
          - connect_for_details: If True, try to connect to each device (default: False)
          - include_classic: If True, include Classic Bluetooth devices (default: True)
          - extended_freebox_detection: If True, use additional methods to detect Freebox (default: True)
          - deduplicate_devices: If True, merge duplicate devices (default: True)
          - parallel_scans: If True, run scans in parallel (default: True)
        
    Returns:
        List of detected devices
        
    Raises:
        HTTPException: On scan error
    """
    try:
        # Use Bluetooth service to perform the scan
        devices = await bluetooth_service.scan_for_devices(
            duration=params.duration, 
            filter_name=params.filter_name,
            connect_for_details=params.connect_for_details,
            include_classic=params.include_classic,
            extended_freebox_detection=params.extended_freebox_detection,
            deduplicate_devices=params.deduplicate_devices,
            parallel_scans=params.parallel_scans
        )
        
        # Return results
        return ScanResponse(devices=devices)
    except BluetoothScanError as e:
        # Convert to HTTPException for FastAPI
        raise HTTPException(status_code=500, detail=str(e))
```

Create session API router:

```python
# app/api/session.py
from fastapi import APIRouter
import uuid
from app.models.session import SessionResponse, bluetooth_scan_tool

# Create FastAPI router
router = APIRouter()

@router.post("/mcp/v1/session", response_model=SessionResponse)
async def create_session():
    """
    Endpoint to initialize an MCP session
    
    Returns:
        Information about the created session and available tools
    """
    # Generate a unique session ID
    session_id = f"bluetooth-session-{uuid.uuid4()}"
    
    # Create response with available tools
    return SessionResponse(
        session={"id": session_id},
        tools=[bluetooth_scan_tool]
    )
```

## 7️⃣ FastAPI Main Application

Create the main FastAPI application:

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import bluetooth, session

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Configure CORS for Claude requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(bluetooth.router)
app.include_router(session.router)

# Server health check route
@app.get("/health")
async def health_check():
    """
    Simple route to check server status
    """
    return {"status": "ok"}
```

Create configuration module:

```python
# app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application configuration"""
    # Application name
    APP_NAME: str = "Bluetooth MCP Server"
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS configuration
    CORS_ORIGINS: list = ["*"]
    
    # Server port
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Server host
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()
```

## 8️⃣ Application Entry Points

Create run.py for starting the FastAPI application:

```python
# run.py
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Start server with configuration parameters
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST, 
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

## 9️⃣ MCP Integration

### MCP SDK Implementation

Create the Bluetooth tool implementation for MCP:

```python
# mcp_sdk/bluetooth_tool.py
from typing import Dict, Any, Optional
from mcp import Tool

class BluetoothTool(Tool):
    """
    Implementation of the Bluetooth tool for the Model Context Protocol
    """
    
    @classmethod
    def get_name(cls) -> str:
        """Tool name"""
        return "bluetooth-scan"
    
    @classmethod
    def get_description(cls) -> str:
        """Tool description"""
        return "Scans for nearby Bluetooth devices (BLE and Classic)"
    
    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Tool parameters"""
        return {
            "type": "object",
            "properties": {
                "duration": {
                    "type": "number",
                    "description": "Scan duration in seconds (default: 5)",
                    "default": 5.0
                },
                "filter_name": {
                    "type": "string",
                    "description": "Optional name filter for devices",
                    "nullable": True
                },
                "include_classic": {
                    "type": "boolean", 
                    "description": "Include classic Bluetooth devices",
                    "default": True
                }
            }
        }
    
    @classmethod
    def execute(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Bluetooth scan
        
        Args:
            params: Scan parameters
        
        Returns:
            Scan results
        """
        import requests
        
        # Bluetooth API URL
        url = "http://localhost:8000/mcp/v1/tools/bluetooth-scan"
        
        try:
            # Default parameters
            scan_params = {
                "duration": params.get("duration", 5.0),
                "filter_name": params.get("filter_name", None),
                "include_classic": params.get("include_classic", True)
            }
            
            # Make request
            response = requests.post(url, json=scan_params)
            response.raise_for_status()
            
            return response.json()
        
        except requests.RequestException as e:
            return {
                "error": f"Bluetooth scan failed: {str(e)}",
                "details": str(e)
            }
```

Initialize MCP SDK:

```python
# mcp_sdk/__init__.py
from .bluetooth_tool import BluetoothTool

__all__ = ['BluetoothTool']
```

### MCP Server Implementation

Create the MCP server implementation:

```python
# bluetooth_mcp_server.py
from mcp.server.fastmcp import FastMCP, Context
import requests
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create MCP server
mcp = FastMCP("Bluetooth MCP Server")

# Get configuration parameters
BLUETOOTH_API_URL = os.getenv('BLUETOOTH_API_URL', 'http://localhost:8000')
BLUETOOTH_SCAN_DURATION = float(os.getenv('BLUETOOTH_SCAN_DURATION', '5.0'))
BLUETOOTH_INCLUDE_CLASSIC = os.getenv('BLUETOOTH_INCLUDE_CLASSIC', 'true').lower() == 'true'

# Register Bluetooth tool
@mcp.tool()
def bluetooth_scan(
    duration: float = BLUETOOTH_SCAN_DURATION, 
    filter_name: Optional[str] = None, 
    include_classic: bool = BLUETOOTH_INCLUDE_CLASSIC
) -> Dict[str, Any]:
    """
    Scan for nearby Bluetooth devices.
    
    Args:
        duration: Scan duration in seconds
        filter_name: Device name filter
        include_classic: Include Classic Bluetooth devices
    
    Returns:
        Bluetooth scan results
    """
    try:
        # Scan parameters
        scan_params = {
            "duration": duration,
            "filter_name": filter_name,
            "include_classic": include_classic
        }
        
        # Make request
        response = requests.post(f"{BLUETOOTH_API_URL}/mcp/v1/tools/bluetooth-scan", json=scan_params)
        response.raise_for_status()
        
        return response.json()
    
    except requests.RequestException as e:
        return {
            "error": f"Bluetooth scan failed: {str(e)}",
            "details": str(e)
        }

# Resource for displaying Bluetooth device information
@mcp.resource("bluetooth://{device_id}")
def get_bluetooth_device_info(device_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific Bluetooth device.
    
    Args:
        device_id: Bluetooth device ID
    
    Returns:
        Detailed device information
    """
    try:
        response = requests.get(f"{BLUETOOTH_API_URL}/mcp/v1/devices/{device_id}")
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as e:
        return {
            "error": f"Could not retrieve device info: {str(e)}",
            "details": str(e)
        }

# Main entry point
if __name__ == "__main__":
    mcp.run()
```

## 🔟 Configuration Files

Create .env.example file:

```
# Debug mode (true/false)
DEBUG=true

# Server configuration
HOST=0.0.0.0
PORT=8000

# CORS origins (comma-separated)
# CORS_ORIGINS=https://claude.ai,http://localhost:3000

# Bluetooth configuration
BLUETOOTH_SCAN_DURATION=5.0
BLUETOOTH_INCLUDE_CLASSIC=true
```

## 🧪 Running the Tests

Run the tests to ensure everything works correctly:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app
```

## 🚀 Running the Servers

### Start the FastAPI Server

```bash
# Using the run.py script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start the MCP Server

```bash
# Start the MCP server
python bluetooth_mcp_server.py
```

## 🔄 Using with Claude

### Expose the Server to the Internet

You can use tools like ngrok to expose your local server:

```bash
ngrok http 8000
```

### Configure Claude to Use Your MCP Server

```bash
npx @anthropic-ai/sdk install-model-context-protocol <YOUR_SERVER_URL>
```

### Test with Claude

Once configured, you can ask Claude to scan for Bluetooth devices:

```
Could you scan for nearby Bluetooth devices?
```

## 🌟 Advanced Features

After implementing the basic functionality, consider adding these advanced features:

### Platform-Specific Optimizations

- **Windows**: Integrate with Windows Registry and WMI for better device detection
- **macOS**: Use CoreBluetooth APIs for enhanced device information
- **Linux**: Leverage BlueZ for deeper Bluetooth stack integration

### Enhanced Device Recognition

- Extend company_identifiers.py with more manufacturer IDs
- Improve mac_prefixes.py to recognize more device types
- Add specialized detection for common devices (TVs, smart home devices, etc.)

### Security Enhancements

- Add authentication to the API endpoints
- Implement rate limiting to prevent abuse
- Add encryption for sensitive device information

### Web UI Dashboard

- Create a simple web UI to visualize detected devices
- Add ability to test scanning directly from the UI
- Provide scan history and device details

## 🔍 Troubleshooting

### Common Issues

#### Bluetooth Adapter Not Found

```bash
# Check if Bluetooth is enabled
sudo systemctl status bluetooth    # Linux
Get-Service bthserv                # Windows
```

#### Permission Denied

Ensure you're running with sufficient privileges:

```bash
# Linux
sudo python run.py

# Windows: Run as Administrator
```

#### No Devices Found

- Ensure devices are powered on and in discoverable mode
- Check if your Bluetooth adapter is working properly
- Try increasing the scan duration

### Debugging Tools

- Enable debug logging in the application
- Use external tools like `bluetoothctl` (Linux) or the Bluetooth debug menu (Windows)
- Check the Bluetooth service status on your system

## 📝 Best Practices

- **Error Handling**: Always handle Bluetooth errors gracefully
- **Logging**: Use detailed logging to help debug issues
- **Timeouts**: Set appropriate timeouts for scanning and connection operations
- **Resource Cleanup**: Always clean up Bluetooth resources properly
- **Validation**: Validate all user inputs to prevent security issues
- **Testing**: Maintain high test coverage, especially for edge cases

## 🔗 Resources

- [Bleak Documentation](https://bleak.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Bluetooth Programming](https://people.csail.mit.edu/albert/bluez-intro/c212.html)
- [Model Context Protocol Documentation](https://github.com/anthropics/anthropic-cookbook/tree/main/model_context_protocol)
- [Bluetooth Core Specification](https://www.bluetooth.com/specifications/specs/)
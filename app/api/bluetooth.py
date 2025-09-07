"""
API entry points for Bluetooth operations.
"""
from fastapi import APIRouter, HTTPException
from app.models.bluetooth import BluetoothScanParams, ScanResponse
from app.services.bluetooth_service import bluetooth_service, BluetoothScanError

# Create FastAPI router
router = APIRouter()


def simplify_devices(devices):
    """
    Simplifies the device list for cleaner JSON output.
    Also sorts by descending RSSI (strongest signal first).
    """
    simplified = [
        {
            "id": getattr(d, "name", None),
            "name": getattr(d, "friendly_name", getattr(d, "address", None)), # get name or friendly-name, fallback to address, or None if any of the info available.
            "address": getattr(d, "address", None),
            "rssi": getattr(d, "rssi", None),
            "manufacturer_data": getattr(d, "manufacturer_data", {})
        }
        for d in devices
    ]
    simplified.sort(key=lambda d: d["rssi"] if d["rssi"] is not None else -999, reverse=True)
    return simplified




@router.post(
    "/mcp/v1/tools/bluetooth-scan",
    response_model=ScanResponse,
    description="Scan nearby Bluetooth devices."
)
async def execute_bluetooth_scan(params: BluetoothScanParams):
    """
    Endpoint to perform a Bluetooth scan.
    
    Args:
        params: Scan parameters, including duration, filters, and options.
    
    Returns:
        List of detected devices.
    
    Raises:
        HTTPException: If an error occurs during scanning.
    """
    try:
        devices = await bluetooth_service.scan_for_devices(
            duration=params.duration,
            filter_name=params.filter_name,
            connect_for_details=params.connect_for_details,
            include_classic=params.include_classic,
            extended_freebox_detection=params.extended_freebox_detection,
            deduplicate_devices=params.deduplicate_devices,
            parallel_scans=params.parallel_scans
        )
        return ScanResponse(devices=simplify_devices(devices))

    except BluetoothScanError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/mcp/v1/tools/bluetooth-scan-fast",
    response_model=ScanResponse,
    description="Quick scan of nearby Bluetooth devices."
)
async def execute_fast_bluetooth_scan(params: BluetoothScanParams = None):
    """
    Endpoint for a fast Bluetooth scan.
    Uses parameters optimised for speed.
    
    Args:
        params: Optional scan parameters.
    
    Returns:
        List of detected devices.
    
    Raises:
        HTTPException: If an error occurs during scanning.
    """
    try:
        if params is None:
            params = BluetoothScanParams()

        # Optimise for speed
        params.parallel_scans = True
        params.duration = params.duration or 3.0
        params.connect_for_details = False

        devices = await bluetooth_service.scan_for_devices(
            duration=params.duration,
            filter_name=params.filter_name,
            connect_for_details=params.connect_for_details,
            include_classic=params.include_classic,
            extended_freebox_detection=params.extended_freebox_detection,
            deduplicate_devices=params.deduplicate_devices,
            parallel_scans=params.parallel_scans
        )
        return ScanResponse(devices=simplify_devices(devices))

    except BluetoothScanError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/mcp/v1/tools/bluetooth-scan-thorough",
    response_model=ScanResponse,
    description="Thorough scan of nearby Bluetooth devices."
)
async def execute_thorough_bluetooth_scan(params: BluetoothScanParams = None):
    """
    Endpoint for a thorough Bluetooth scan.
    Uses parameters optimised to detect as many devices as possible.
    
    Args:
        params: Optional scan parameters.
    
    Returns:
        List of detected devices.
    
    Raises:
        HTTPException: If an error occurs during scanning.
    """
    try:
        if params is None:
            params = BluetoothScanParams()

        # Parameters for complete detection
        params.duration = params.duration or 10.0
        params.include_classic = True
        params.extended_freebox_detection = True
        params.deduplicate_devices = True
        params.connect_for_details = True

        devices = await bluetooth_service.scan_for_devices(
            duration=params.duration,
            filter_name=params.filter_name,
            connect_for_details=params.connect_for_details,
            include_classic=params.include_classic,
            extended_freebox_detection=params.extended_freebox_detection,
            deduplicate_devices=params.deduplicate_devices,
            parallel_scans=params.parallel_scans
        )
        return ScanResponse(devices=simplify_devices(devices))

    except BluetoothScanError as e:
        raise HTTPException(status_code=500, detail=str(e))

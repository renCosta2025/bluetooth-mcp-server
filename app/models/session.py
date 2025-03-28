"""
Modèles de données pour les sessions MCP.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any

class SessionResponse(BaseModel):
    """Réponse pour la création d'une session MCP"""
    session: Dict[str, str]
    tools: List[Dict[str, Any]]
    
    @validator('session')
    def session_must_have_id(cls, v):
        """Validation pour s'assurer que la session a un ID"""
        if 'id' not in v or not v['id']:
            raise ValueError('La session doit avoir un ID')
        return v

# Définition des outils MCP disponibles
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
                "description": "If true, includes classic Bluetooth devices in the scan results (recommended to find all devices, including Freebox)"
            },
            "extended_freebox_detection": {
                "type": "boolean",
                "description": "If true, uses additional methods to detect Freebox devices (recommended for Freebox detection)"
            },
            "deduplicate_devices": {
                "type": "boolean",
                "description": "If true, merges duplicate devices with the same MAC address or similar attributes (recommended)"
            },
            "parallel_scans": {
                "type": "boolean",
                "description": "If true, executes different scan methods in parallel for faster results (default: true)"
            }
        }
    }
}
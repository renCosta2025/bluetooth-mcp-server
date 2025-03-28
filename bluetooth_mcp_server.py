from mcp.server.fastmcp import FastMCP, Context
import requests
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Importer votre outil Bluetooth existant
from mcp_sdk.bluetooth_tool import BluetoothTool

# Créer le serveur MCP
mcp = FastMCP("Bluetooth MCP Server")

# Récupérer les paramètres de configuration
BLUETOOTH_API_URL = os.getenv('BLUETOOTH_API_URL', 'http://localhost:8000')
BLUETOOTH_SCAN_DURATION = float(os.getenv('BLUETOOTH_SCAN_DURATION', '5.0'))
BLUETOOTH_INCLUDE_CLASSIC = os.getenv('BLUETOOTH_INCLUDE_CLASSIC', 'true').lower() == 'true'

# Enregistrer l'outil Bluetooth
@mcp.tool()
def bluetooth_scan(
    duration: float = BLUETOOTH_SCAN_DURATION, 
    filter_name: Optional[str] = None, 
    include_classic: bool = BLUETOOTH_INCLUDE_CLASSIC
) -> Dict[str, Any]:
    """
    Effectue un scan des appareils Bluetooth à proximité.
    
    Args:
        duration: Durée du scan en secondes
        filter_name: Nom de l'appareil à filtrer
        include_classic: Inclure les appareils Bluetooth classiques
    
    Returns:
        Résultats du scan Bluetooth
    """
    try:
        # Paramètres du scan
        scan_params = {
            "duration": duration,
            "filter_name": filter_name,
            "include_classic": include_classic
        }
        
        # Effectuer la requête
        response = requests.post(f"{BLUETOOTH_API_URL}/mcp/v1/tools/bluetooth-scan", json=scan_params)
        response.raise_for_status()
        
        return response.json()
    
    except requests.RequestException as e:
        return {
            "error": f"Bluetooth scan failed: {str(e)}",
            "details": str(e)
        }

# Ressource pour afficher des informations sur les appareils Bluetooth
@mcp.resource("bluetooth://{device_id}")
def get_bluetooth_device_info(device_id: str) -> Dict[str, Any]:
    """
    Récupère les informations détaillées d'un appareil Bluetooth spécifique.
    
    Args:
        device_id: Identifiant de l'appareil Bluetooth
    
    Returns:
        Informations détaillées de l'appareil
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

# Point d'entrée principal
if __name__ == "__main__":
    mcp.run()
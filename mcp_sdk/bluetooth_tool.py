from typing import Dict, Any, Optional
from mcp import Tool

class BluetoothTool(Tool):
    """
    Implémentation de l'outil Bluetooth pour le Model Context Protocol
    """
    
    @classmethod
    def get_name(cls) -> str:
        """Nom de l'outil"""
        return "bluetooth-scan"
    
    @classmethod
    def get_description(cls) -> str:
        """Description de l'outil"""
        return "Scans for nearby Bluetooth devices (BLE and Classic)"
    
    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Paramètres de l'outil"""
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
        Exécute le scan Bluetooth
        
        Args:
            params: Paramètres du scan
        
        Returns:
            Résultats du scan
        """
        import requests
        
        # URL de l'API Bluetooth
        url = "http://localhost:8000/mcp/v1/tools/bluetooth-scan"
        
        try:
            # Paramètres par défaut
            scan_params = {
                "duration": params.get("duration", 5.0),
                "filter_name": params.get("filter_name", None),
                "include_classic": params.get("include_classic", True)
            }
            
            # Effectuer la requête
            response = requests.post(url, json=scan_params)
            response.raise_for_status()  # Lever une exception pour les codes d'erreur
            
            return response.json()
        
        except requests.RequestException as e:
            return {
                "error": f"Bluetooth scan failed: {str(e)}",
                "details": str(e)
            }
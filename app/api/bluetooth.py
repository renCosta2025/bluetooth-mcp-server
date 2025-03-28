"""
Points d'entrée API pour les opérations Bluetooth.
"""
from fastapi import APIRouter, HTTPException, Query
from app.models.bluetooth import BluetoothScanParams, ScanResponse
from app.services.bluetooth_service import bluetooth_service, BluetoothScanError

# Création du router FastAPI
router = APIRouter()

@router.post("/mcp/v1/tools/bluetooth-scan", response_model=ScanResponse, 
             description="Scanne les appareils Bluetooth à proximité. "
                         "Utilisez filter_name=null ou omettez le champ pour voir tous les appareils.")
async def execute_bluetooth_scan(params: BluetoothScanParams):
    """
    Endpoint pour exécuter l'outil de scan Bluetooth.
    Détecte les appareils BLE et Bluetooth classiques à proximité.
    
    Args:
        params: Paramètres pour le scan
          - duration: Durée du scan en secondes (défaut: 5.0)
          - filter_name: Filtre optionnel sur le nom des appareils (null pour voir tous les appareils)
          - connect_for_details: Si True, tente de se connecter à chaque appareil (défaut: False)
          - include_classic: Si True, inclut les appareils Bluetooth classiques (défaut: True)
          - extended_freebox_detection: Si True, utilise des méthodes supplémentaires pour détecter les Freebox (défaut: True)
        
    Returns:
        Liste des appareils détectés
        
    Raises:
        HTTPException: En cas d'erreur pendant le scan
    """
    try:
        # Utilisation du service Bluetooth pour effectuer le scan
        devices = await bluetooth_service.scan_for_devices(
            duration=params.duration, 
            filter_name=params.filter_name,
            connect_for_details=params.connect_for_details,
            include_classic=params.include_classic,
            extended_freebox_detection=params.extended_freebox_detection
        )
        
        # Retourne les résultats
        return ScanResponse(devices=devices)
    except BluetoothScanError as e:
        # Conversion en HTTPException pour FastAPI
        raise HTTPException(status_code=500, detail=str(e))
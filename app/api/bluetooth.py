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
          - deduplicate_devices: Si True, fusionne les appareils en double (défaut: True)
          - parallel_scans: Si True, exécute les scans en parallèle (défaut: True)
        
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
            extended_freebox_detection=params.extended_freebox_detection,
            deduplicate_devices=params.deduplicate_devices,
            parallel_scans=params.parallel_scans
        )
        
        # Retourne les résultats
        return ScanResponse(devices=devices)
    except BluetoothScanError as e:
        # Conversion en HTTPException pour FastAPI
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp/v1/tools/bluetooth-scan-fast", response_model=ScanResponse, 
             description="Scanne les appareils Bluetooth à proximité avec des paramètres optimisés pour la rapidité.")
async def execute_fast_bluetooth_scan(params: BluetoothScanParams = None):
    """
    Endpoint pour un scan Bluetooth rapide.
    Utilise des paramètres optimisés pour une détection rapide des appareils.
    
    Args:
        params: Paramètres pour le scan (optionnel)
        
    Returns:
        Liste des appareils détectés
        
    Raises:
        HTTPException: En cas d'erreur pendant le scan
    """
    try:
        # Utiliser des paramètres par défaut optimisés pour la rapidité
        if params is None:
            params = BluetoothScanParams()
        
        # Forcer l'utilisation des scans parallèles pour une meilleure performance
        params.parallel_scans = True
        params.duration = params.duration or 3.0  # Scan plus court
        params.connect_for_details = False  # Pas de connexion pour plus de rapidité
        
        # Utilisation du service Bluetooth pour effectuer le scan
        devices = await bluetooth_service.scan_for_devices(
            duration=params.duration, 
            filter_name=params.filter_name,
            connect_for_details=params.connect_for_details,
            include_classic=params.include_classic,
            extended_freebox_detection=params.extended_freebox_detection,
            deduplicate_devices=params.deduplicate_devices,
            parallel_scans=params.parallel_scans
        )
        
        # Retourne les résultats
        return ScanResponse(devices=devices)
    except BluetoothScanError as e:
        # Conversion en HTTPException pour FastAPI
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp/v1/tools/bluetooth-scan-thorough", response_model=ScanResponse, 
             description="Scanne les appareils Bluetooth à proximité avec des paramètres optimisés pour une détection complète.")
async def execute_thorough_bluetooth_scan(params: BluetoothScanParams = None):
    """
    Endpoint pour un scan Bluetooth approfondi.
    Utilise des paramètres optimisés pour détecter un maximum d'appareils, y compris les plus difficiles à détecter.
    
    Args:
        params: Paramètres pour le scan (optionnel)
        
    Returns:
        Liste des appareils détectés
        
    Raises:
        HTTPException: En cas d'erreur pendant le scan
    """
    try:
        # Utiliser des paramètres par défaut optimisés pour une détection complète
        if params is None:
            params = BluetoothScanParams()
        
        # Forcer l'utilisation des paramètres optimaux pour une détection approfondie
        params.duration = params.duration or 10.0  # Scan plus long
        params.include_classic = True  # Activer le scan classique
        params.extended_freebox_detection = True  # Activer la détection étendue
        params.deduplicate_devices = True  # Activer la déduplication
        params.connect_for_details = True  # Activer la connexion pour plus de détails
        
        # Utilisation du service Bluetooth pour effectuer le scan
        devices = await bluetooth_service.scan_for_devices(
            duration=params.duration, 
            filter_name=params.filter_name,
            connect_for_details=params.connect_for_details,
            include_classic=params.include_classic,
            extended_freebox_detection=params.extended_freebox_detection,
            deduplicate_devices=params.deduplicate_devices,
            parallel_scans=params.parallel_scans
        )
        
        # Retourne les résultats
        return ScanResponse(devices=devices)
    except BluetoothScanError as e:
        # Conversion en HTTPException pour FastAPI
        raise HTTPException(status_code=500, detail=str(e))
# Guide d'implémentation d'un serveur MCP pour la détection Bluetooth

Ce document détaille les étapes nécessaires pour créer un serveur ModelContextProtocol (MCP) qui permet à Claude AI de détecter les appareils Bluetooth à proximité. L'implémentation est basée sur Python avec FastAPI et Bleak pour la gestion du Bluetooth, suivant l'approche TDD (Test-Driven Development).

## Prérequis

- Python 3.7+ installé
- Un adaptateur Bluetooth compatible (intégré ou externe)
- Droits administrateur/sudo (nécessaires pour certaines opérations Bluetooth)
- Connexion Internet (pour l'installation des packages)

## 1. Configuration de l'environnement

### Création d'un environnement virtuel

```bash
# Créer un dossier pour le projet
mkdir bluetooth-mcp
cd bluetooth-mcp

# Créer et activer un environnement virtuel
python -m venv venv

# Sur Windows
venv\Scripts\activate

# Sur macOS/Linux
source venv/bin/activate
Installation des dépendances
bashCopier# Installer les dépendances de base
pip install fastapi uvicorn bleak pydantic python-dotenv pytest pytest-asyncio httpx

# Sur les systèmes non-Windows, pour le support Bluetooth classique (optionnel)
pip install pybluez2

# Pour le support MCP
pip install model-context-protocol-sdk
2. Approche TDD
Suivant l'approche TDD, nous commençons par écrire les tests avant l'implémentation :

Écrire les tests pour les fonctionnalités à implémenter
Vérifier que les tests échouent (puisque le code n'est pas encore implémenté)
Implémenter le code minimal pour faire passer les tests
Refactoriser le code si nécessaire
Répéter pour chaque nouvelle fonctionnalité

Exemple de test pour le modèle BluetoothDevice
pythonCopier# tests/models/test_bluetooth_model.py
import pytest
from pydantic import ValidationError

def test_bluetooth_device_model():
    """Test pour vérifier que le modèle BluetoothDevice fonctionne correctement"""
    # Importation du modèle
    from app.models.bluetooth import BluetoothDevice
    
    # Test avec des données valides
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
3. Structure du projet
Organisez votre projet selon l'architecture définie dans architecture.md. Voici les composants clés à implémenter :
A. Modèles de données
Créez les modèles Pydantic pour représenter les appareils Bluetooth et les paramètres de scan :
pythonCopier# app/models/bluetooth.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any

class BluetoothDevice(BaseModel):
    """Modèle représentant un appareil Bluetooth détecté"""
    id: str
    address: str
    name: str
    rssi: Optional[int] = None
    manufacturer_data: Optional[Dict[int, List[int]]] = None
    service_uuids: Optional[List[str]] = None
    device_type: Optional[str] = None
    company_name: Optional[str] = None
    friendly_name: Optional[str] = None

class BluetoothScanParams(BaseModel):
    """Paramètres pour le scan d'appareils Bluetooth"""
    duration: Optional[float] = 5.0
    filter_name: Optional[str] = None
    include_classic: Optional[bool] = True
    
    @validator('duration')
    def duration_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('La durée doit être positive')
        return v

class ScanResponse(BaseModel):
    """Réponse contenant la liste des appareils Bluetooth détectés"""
    devices: List[BluetoothDevice]
B. Services
Implémentez les services qui effectuent le scan Bluetooth :
pythonCopier# app/services/bluetooth_service.py
import logging
import asyncio
from typing import List, Optional
from bleak import BleakScanner

from app.models.bluetooth import BluetoothDevice
from app.utils.bluetooth_utils import format_manufacturer_data

class BluetoothScanError(Exception):
    """Exception personnalisée pour les erreurs de scan Bluetooth"""
    pass

class BluetoothService:
    """Service pour gérer les opérations Bluetooth"""
    
    async def scan_for_devices(self, duration: float = 5.0, filter_name: Optional[str] = None) -> List[BluetoothDevice]:
        """
        Effectue un scan des appareils Bluetooth à proximité
        
        Args:
            duration: Durée du scan en secondes
            filter_name: Filtre optionnel sur le nom des appareils
            
        Returns:
            Liste des appareils Bluetooth détectés
            
        Raises:
            BluetoothScanError: En cas d'erreur pendant le scan
        """
        try:
            # Utilisation de BleakScanner pour la découverte d'appareils
            devices = []
            discovered_devices = await BleakScanner.discover(timeout=duration)
            
            for device in discovered_devices:
                device_name = device.name or "Unknown"
                
                # Appliquer le filtre si nécessaire
                if filter_name is None or (filter_name.lower() in device_name.lower()):
                    # Créer un objet BluetoothDevice
                    bluetooth_device = BluetoothDevice(
                        id=str(device.address),
                        address=device.address,
                        name=device_name,
                        rssi=device.rssi or 0,
                        manufacturer_data=format_manufacturer_data(getattr(device, 'metadata', {}).get('manufacturer_data', {})),
                        service_uuids=getattr(device, 'metadata', {}).get('service_uuids', [])
                    )
                    
                    devices.append(bluetooth_device)
            
            return devices
        except Exception as e:
            raise BluetoothScanError(f"Erreur lors du scan Bluetooth: {str(e)}")

# Création d'une instance du service pour pouvoir l'importer facilement
bluetooth_service = BluetoothService()
C. API Endpoints
Créez les endpoints FastAPI pour exposer les fonctionnalités Bluetooth :
pythonCopier# app/api/bluetooth.py
from fastapi import APIRouter, HTTPException
from app.models.bluetooth import BluetoothScanParams, ScanResponse
from app.services.bluetooth_service import bluetooth_service, BluetoothScanError

# Création du router FastAPI
router = APIRouter()

@router.post("/mcp/v1/tools/bluetooth-scan", response_model=ScanResponse)
async def execute_bluetooth_scan(params: BluetoothScanParams):
    """
    Endpoint pour exécuter l'outil de scan Bluetooth
    
    Args:
        params: Paramètres pour le scan
        
    Returns:
        Liste des appareils détectés
        
    Raises:
        HTTPException: En cas d'erreur pendant le scan
    """
    try:
        # Utilisation du service Bluetooth pour effectuer le scan
        devices = await bluetooth_service.scan_for_devices(
            duration=params.duration, 
            filter_name=params.filter_name
        )
        
        # Retourne les résultats
        return ScanResponse(devices=devices)
    except BluetoothScanError as e:
        # Conversion en HTTPException pour FastAPI
        raise HTTPException(status_code=500, detail=str(e))
D. MCP Integration
Implémentez l'intégration MCP pour permettre à Claude d'utiliser l'outil Bluetooth :
pythonCopier# bluetooth_mcp_server.py
from mcp.server.fastmcp import FastMCP, Context
import requests
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Créer le serveur MCP
mcp = FastMCP("Bluetooth MCP Server")

# Récupérer les paramètres de configuration
BLUETOOTH_API_URL = os.getenv('BLUETOOTH_API_URL', 'http://localhost:8000')

# Enregistrer l'outil Bluetooth
@mcp.tool()
def bluetooth_scan(duration: float = 5.0, filter_name: Optional[str] = None, include_classic: bool = True) -> Dict[str, Any]:
    """
    Effectue un scan des appareils Bluetooth à proximité
    
    Args:
        duration: Durée du scan en secondes
        filter_name: Filtre optionnel sur le nom des appareils
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

# Point d'entrée principal
if __name__ == "__main__":
    mcp.run()
4. Exécution des tests
Une fois que vous avez implémenté les composants de base, exécutez les tests pour vérifier que tout fonctionne correctement :
bashCopier# Exécuter tous les tests
pytest

# Exécuter des tests spécifiques
pytest tests/models/  # Tests des modèles
pytest tests/api/  # Tests des API
pytest tests/services/  # Tests des services
5. Exécution du serveur
API Bluetooth
bashCopier# Démarrer le serveur FastAPI
python run.py
Serveur MCP
bashCopier# Démarrer le serveur MCP
python bluetooth_mcp_server.py
6. Utilisation avec Claude

Exposez votre serveur MCP à Internet (par exemple, avec ngrok) :
bashCopierngrok http 8000

Configurez le MCP dans Claude :
bashCopiernpx @anthropic-ai/sdk install-model-context-protocol <URL_DU_SERVEUR>

Maintenant, vous pouvez demander à Claude de scanner les appareils Bluetooth :
CopierPeux-tu scanner les appareils Bluetooth à proximité ?


7. Fonctionnalités avancées
Après avoir implémenté les fonctionnalités de base, vous pouvez ajouter des améliorations :

Support multiplateforme : Optimisations pour Windows, Linux, et macOS
Détection Bluetooth classique : Ajout du support pour les appareils non-BLE
Détection d'appareils spéciaux : Identification des TV, Freebox, etc.
Interface utilisateur web : Panel d'administration pour tester le serveur
Authentification : Sécurisation des API avec des tokens

8. Bonnes pratiques

Logging : Utilisez le module logging pour suivre l'exécution
Documentation : Documentez votre code avec des docstrings
Gestion des erreurs : Implémentez une gestion robuste des exceptions
Configuration : Utilisez des variables d'environnement pour les paramètres
Tests : Maintenez une couverture de tests élevée

9. Dépannage
Problèmes Bluetooth

Permissions : Sur Linux, assurez-vous d'avoir les permissions nécessaires (sudo)
Adaptateur : Vérifiez que le Bluetooth est activé et que l'adaptateur est reconnu
Windows : Vérifiez les services Bluetooth dans le gestionnaire de services

Problèmes MCP

URL : Assurez-vous que l'URL du serveur MCP est accessible
Formats : Vérifiez que les réponses suivent le format attendu par Claude
Timeout : Ajustez les timeouts pour les scans longs

10. Ressources

Documentation Bleak
Documentation FastAPI
Documentation MCP
Spécification Bluetooth


Ce guide vous offre un point de départ complet pour implémenter un serveur MCP Bluetooth. N'hésitez pas à l'adapter à vos besoins spécifiques et à explorer les fonctionnalités avancées de Bluetooth pour enrichir votre implémentation.
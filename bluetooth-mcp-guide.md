# Guide d'implémentation d'un serveur MCP pour la détection Bluetooth

Ce document détaille les étapes nécessaires pour créer un serveur ModelContextProtocol (MCP) qui permet à Claude AI de détecter les appareils Bluetooth à proximité. L'implémentation est basée sur Python avec FastAPI et la bibliothèque Bleak pour la gestion du Bluetooth.

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
```

### Installation des dépendances

```bash
pip install fastapi uvicorn pydantic bleak
```

## 2. Structure du projet

Créez les fichiers suivants dans votre dossier de projet :

### `main.py` - Point d'entrée principal

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uuid
from bleak import BleakScanner

app = FastAPI(title="Bluetooth MCP Server")

# Configuration CORS pour permettre les requêtes depuis Claude
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données
class SessionResponse(BaseModel):
    session: Dict[str, str]
    tools: List[Dict[str, Any]]

class BluetoothScanParams(BaseModel):
    duration: Optional[float] = 5.0
    filter_name: Optional[str] = None

class BluetoothDevice(BaseModel):
    id: str
    address: str
    name: str
    rssi: int

class ScanResponse(BaseModel):
    devices: List[BluetoothDevice]

# Définition des outils MCP
bluetooth_scan_tool = {
    "name": "bluetooth-scan",
    "description": "Scans for nearby Bluetooth devices",
    "parameters": {
        "type": "object",
        "properties": {
            "duration": {
                "type": "number",
                "description": "Scan duration in seconds (default: 5)"
            },
            "filter_name": {
                "type": "string",
                "description": "Optional name filter for devices"
            }
        }
    }
}

# Fonction pour scanner les appareils Bluetooth
async def scan_for_devices(duration: float = 5.0, filter_name: Optional[str] = None):
    devices = []
    try:
        # Utilisation de BleakScanner pour la découverte d'appareils
        discovered_devices = await BleakScanner.discover(timeout=duration)
        
        for device in discovered_devices:
            device_name = device.name or "Unknown"
            
            # Appliquer le filtre si nécessaire
            if filter_name is None or (filter_name.lower() in device_name.lower()):
                devices.append(BluetoothDevice(
                    id=str(device.address),
                    address=device.address,
                    name=device_name,
                    rssi=device.rssi or 0
                ))
                
        return devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bluetooth scan error: {str(e)}")

# Endpoint pour initialiser une session MCP
@app.post("/mcp/v1/session", response_model=SessionResponse)
async def create_session():
    session_id = f"bluetooth-session-{uuid.uuid4()}"
    return SessionResponse(
        session={"id": session_id},
        tools=[bluetooth_scan_tool]
    )

# Endpoint pour exécuter l'outil de scan Bluetooth
@app.post("/mcp/v1/tools/bluetooth-scan", response_model=ScanResponse)
async def execute_bluetooth_scan(params: BluetoothScanParams):
    devices = await scan_for_devices(params.duration, params.filter_name)
    return ScanResponse(devices=devices)

# Pour tester localement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 3. Lancement du serveur MCP

### Démarrage local

```bash
# À partir du dossier du projet avec l'environnement virtuel activé
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Vérification du fonctionnement

Accédez à l'URL suivante dans votre navigateur pour vérifier que le serveur fonctionne et consulter la documentation API :
```
http://localhost:8000/docs
```

## 4. Exposition du serveur pour Claude

Pour que Claude puisse communiquer avec votre serveur MCP, vous devez le rendre accessible depuis Internet. Plusieurs options sont possibles :

### Option 1 : Tunneling avec ngrok (pour les tests)

1. Installez ngrok (https://ngrok.com/download)
2. Exécutez la commande suivante dans un nouveau terminal :
   ```bash
   ngrok http 8000
   ```
3. Notez l'URL fournie par ngrok (ex: https://abcd1234.ngrok.io)

### Option 2 : Déploiement sur un serveur

Vous pouvez déployer l'application sur un serveur avec une adresse IP publique, en utilisant un service comme :
- Heroku
- DigitalOcean
- AWS
- etc.

N'oubliez pas de configurer les pare-feu pour autoriser le port utilisé.

## 5. Configuration du MCP dans Claude

1. Utilisez l'URL de votre serveur (obtenue à l'étape 4) pour configurer le MCP dans Claude
2. Pour utiliser le MCP avec Claude dans une conversation, vous pouvez exécuter :
   ```
   npx @anthropic-ai/sdk install-model-context-protocol <URL_DE_VOTRE_SERVEUR>
   ```

## 6. Dépannage courant

### Problèmes Bluetooth

- **Erreur "Access denied"** : Exécutez le serveur avec des privilèges administrateur ou sudo
- **Adaptateur non détecté** : Vérifiez que le Bluetooth est activé et que l'adaptateur est reconnu par le système
- **Scan ne trouve aucun appareil** : Assurez-vous que des appareils Bluetooth à proximité sont en mode découvrable

### Problèmes de serveur

- **Erreur de port déjà utilisé** : Changez le port dans la commande uvicorn (ex: --port 8080)
- **Timeout des requêtes** : Augmentez la durée de timeout dans la configuration de FastAPI

## 7. Extensions futures

Une fois que la détection d'appareils fonctionne, vous pourriez étendre le MCP avec :

1. **Connexion aux appareils** : Ajoutez un outil pour se connecter à un appareil spécifique
2. **Lecture/écriture** : Implémentez des fonctions pour lire et écrire des caractéristiques GATT
3. **Contrôle d'appareils** : Ajoutez des commandes spécifiques pour différents types d'appareils (lumières, capteurs, etc.)

## 8. Remarques importantes

- Le Bluetooth LE (Low Energy) et le Bluetooth classique ont des APIs différentes. Cette implémentation se concentre sur le Bluetooth LE avec Bleak
- Les capacités Bluetooth varient selon les systèmes d'exploitation et les adaptateurs
- Pour une utilisation en production, ajoutez des mécanismes d'authentification et de sécurité appropriés

---

Ce guide couvre les bases de l'implémentation d'un serveur MCP pour la détection Bluetooth. Pour toute question ou problème spécifique, n'hésitez pas à consulter la documentation officielle des bibliothèques utilisées ou à demander de l'aide à Claude.

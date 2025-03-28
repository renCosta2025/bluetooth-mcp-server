# Serveur MCP Bluetooth

Ce projet est un serveur ModelContextProtocol (MCP) qui permet à Claude AI de détecter les appareils Bluetooth à proximité.

## Fonctionnalités

- Scanner les appareils Bluetooth à proximité
- Filtrer les appareils par nom
- Interface MCP compatible avec Claude AI

## Prérequis

- Python 3.7+
- Un adaptateur Bluetooth compatible (intégré ou externe)
- Droits administrateur/sudo (nécessaires pour certaines opérations Bluetooth)
- Connexion Internet (pour l'installation des packages)

## Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-username/bluetooth-mcp-server.git
   cd bluetooth-mcp-server
   ```

2. Créer et activer un environnement virtuel :
   ```bash
   # Créer l'environnement virtuel
   python -m venv venv

   # Activer l'environnement virtuel
   # Sur Windows
   venv\Scripts\activate
   # Sur macOS/Linux
   source venv/bin/activate
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les variables d'environnement :
   ```bash
   # Copier le fichier d'exemple
   cp .env.example .env
   
   # Éditer selon vos besoins
   nano .env
   ```

## Démarrage du serveur

```bash
# Méthode simple
python run.py

# Alternative avec uvicorn directement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Utilisation avec Claude

1. Exposer le serveur à Internet via ngrok ou un déploiement sur un serveur :
   ```bash
   ngrok http 8000
   ```

2. Configurer le MCP dans Claude :
   ```bash
   npx @anthropic-ai/sdk install-model-context-protocol <URL_DU_SERVEUR>
   ```

3. Utiliser Claude avec les capacités Bluetooth

## Tests

Pour exécuter les tests :

```bash
pytest
```

## Structure du projet

```
bluetooth-mcp-server/            # Dossier racine du projet
│
├── app/                         # Package principal de l'application
│   ├── __init__.py             # Initialise le package app
│   ├── main.py                 # Point d'entrée de l'application FastAPI
│   │
│   ├── api/                    # Sous-package pour les points d'entrée API
│   │   ├── __init__.py        # Initialise le package api
│   │   ├── bluetooth.py       # Endpoints pour les opérations Bluetooth
│   │   └── session.py         # Endpoints pour la gestion des sessions MCP
│   │
│   ├── core/                   # Sous-package pour la configuration centrale
│   │   ├── __init__.py        # Initialise le package core
│   │   └── config.py          # Configuration de l'application
│   │
│   ├── models/                 # Sous-package pour les modèles de données
│   │   ├── __init__.py        # Initialise le package models
│   │   ├── bluetooth.py       # Modèles pour les données Bluetooth
│   │   └── session.py         # Modèles pour les données de session
│   │
│   ├── services/               # Sous-package pour la logique métier
│   │   ├── __init__.py        # Initialise le package services
│   │   └── bluetooth_service.py # Service pour les opérations Bluetooth
│   │
│   └── utils/                  # Sous-package pour les utilitaires
│       └── __init__.py        # Initialise le package utils
│
├── tests/                      # Tests unitaires et d'intégration
│
├── .env                        # Variables d'environnement (local)
├── .env.example                # Exemple de variables d'environnement
├── README.md                   # Documentation du projet
├── requirements.txt            # Dépendances du projet
└── run.py                      # Script pour démarrer l'application
```

## Dépannage

### Problèmes Bluetooth

- **Erreur "Access denied"** : Exécutez le serveur avec des privilèges administrateur ou sudo
- **Adaptateur non détecté** : Vérifiez que le Bluetooth est activé
- **Scan ne trouve aucun appareil** : Assurez-vous que des appareils Bluetooth à proximité sont en mode découvrable

## Licence

MIT
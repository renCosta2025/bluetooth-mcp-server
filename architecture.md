# architecture.md

```markdown
# Structure du Projet Bluetooth MCP Server

Ce document présente la structure organisationnelle du projet de serveur MCP pour la détection Bluetooth.
bluetooth-mcp-server/            # Dossier racine du projet
│
├── app/                         # Package principal de l'application
│   ├── init.py             # Initialise le package app
│   ├── main.py                 # Point d'entrée de l'application FastAPI
│   │
│   ├── api/                    # Sous-package pour les points d'entrée API
│   │   ├── init.py        # Initialise le package api
│   │   ├── bluetooth.py       # Endpoints pour les opérations Bluetooth
│   │   └── session.py         # Endpoints pour la gestion des sessions MCP
│   │
│   ├── core/                   # Sous-package pour la configuration centrale
│   │   ├── init.py        # Initialise le package core
│   │   └── config.py          # Configuration de l'application
│   │
│   ├── data/                   # Sous-package pour les données statiques
│   │   ├── init.py        # Initialise le package data
│   │   ├── company_identifiers.py  # Base de données des identifiants de fabricants
│   │   └── mac_prefixes.py    # Base de données des préfixes d'adresses MAC
│   │
│   ├── models/                 # Sous-package pour les modèles de données
│   │   ├── init.py        # Initialise le package models
│   │   ├── bluetooth.py       # Modèles pour les données Bluetooth
│   │   └── session.py         # Modèles pour les données de session
│   │
│   ├── services/               # Sous-package pour la logique métier
│   │   ├── init.py        # Initialise le package services
│   │   ├── bluetooth_service.py # Service principal pour les opérations Bluetooth
│   │   ├── ble_scanner.py     # Scanner BLE
│   │   ├── classic_scanner.py # Scanner Bluetooth classique
│   │   ├── windows_scanner.py # Scanner Bluetooth spécifique à Windows
│   │   └── windows_advanced_scanner.py # Scanner avancé pour Windows
│   │
│   └── utils/                  # Sous-package pour les utilitaires
│       ├── init.py        # Initialise le package utils
│       └── bluetooth_utils.py # Utilitaires pour le traitement des données Bluetooth
│
├── mcp_sdk/                    # Package pour le SDK MCP
│   ├── init.py            # Initialise le package mcp_sdk
│   ├── bluetooth_tool.py      # Implémentation de l'outil Bluetooth pour MCP
│   ├── setup.py               # Configuration pour l'installation du package
│   └── tests/                 # Tests pour le SDK
│       ├── init.py        # Initialise le package tests
│       └── test_bluetooth_tool.py # Tests pour l'outil Bluetooth
│
├── tests/                      # Tests unitaires et d'intégration
│   ├── init.py            # Initialise le package tests
│   ├── test_main.py           # Tests pour l'application principale
│   ├── TEST.md                # Documentation sur l'état des tests
│   │
│   ├── api/                   # Tests pour les API
│   │   ├── init.py        # Initialise le package tests.api
│   │   ├── test_bluetooth.py  # Tests pour l'API Bluetooth
│   │   └── test_session.py    # Tests pour l'API Session
│   │
│   ├── models/                # Tests pour les modèles
│   │   ├── init.py        # Initialise le package tests.models
│   │   ├── test_bluetooth_model.py # Tests pour les modèles Bluetooth
│   │   └── test_session_model.py # Tests pour les modèles Session
│   │
│   ├── services/              # Tests pour les services
│   │   ├── init.py        # Initialise le package tests.services
│   │   ├── test_bluetooth_service.py # Tests pour le service Bluetooth
│   │   └── test_classic_bluetooth.py # Tests pour le scanner Bluetooth classique
│   │
│   └── utils/                 # Tests pour les utilitaires
│       ├── init.py        # Initialise le package tests.utils
│       └── test_bluetooth_utils.py # Tests pour les utilitaires Bluetooth
│
├── .env                        # Variables d'environnement (local)
├── .env.example                # Exemple de variables d'environnement
├── run.py                      # Script pour démarrer l'application
├── bluetooth_mcp_server.py     # Script pour démarrer le serveur MCP
├── architecture.md             # Documentation de l'architecture
├── bluetooth-mcp-guide.md      # Guide d'implémentation du serveur MCP
├── requirements.txt            # Dépendances du projet
└── README.md                   # Documentation du projet
Copier
## Description des composants principaux

### Fichiers racine
- **run.py**: Script de démarrage du serveur FastAPI
- **bluetooth_mcp_server.py**: Script de démarrage du serveur MCP intégré avec l'API Bluetooth
- **.env**: Configuration des variables d'environnement (non versionné)
- **.env.example**: Exemple de configuration des variables d'environnement
- **requirements.txt**: Liste des dépendances Python
- **README.md**: Documentation principale du projet
- **architecture.md**: Documentation de la structure du projet
- **bluetooth-mcp-guide.md**: Guide détaillé d'implémentation

### Package app
- **main.py**: Configure et initialise l'application FastAPI

### Sous-package api
- **bluetooth.py**: Endpoints pour les opérations de scan Bluetooth
- **session.py**: Endpoints pour la gestion des sessions MCP

### Sous-package data
- **company_identifiers.py**: Base de données des identifiants de fabricants Bluetooth
- **mac_prefixes.py**: Base de données des préfixes d'adresses MAC pour identifier les appareils

### Sous-package models
- **bluetooth.py**: Modèles Pydantic pour les données Bluetooth
- **session.py**: Modèles Pydantic pour les sessions MCP

### Sous-package services
- **bluetooth_service.py**: Service principal orchestrant les différents scanners
- **ble_scanner.py**: Scanner pour les appareils BLE (Bluetooth Low Energy)
- **classic_scanner.py**: Scanner pour les appareils Bluetooth classiques
- **windows_scanner.py**: Scanner spécifique pour Windows
- **windows_advanced_scanner.py**: Scanner avancé pour Windows utilisant des API natives

### Sous-package utils
- **bluetooth_utils.py**: Fonctions utilitaires pour le traitement des données Bluetooth

### Package mcp_sdk
- **bluetooth_tool.py**: Implémentation de l'outil Bluetooth pour le SDK MCP
- **setup.py**: Configuration pour l'installation du package SDK
{
  `content`: `# Structure du Projet Bluetooth MCP Server

Ce document présente la structure organisationnelle du projet de serveur MCP pour la détection Bluetooth.

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
├── venv/                       # Environnement virtuel Python (généré)
│
├── .env                        # Variables d'environnement (local)
├── .env.example                # Exemple de variables d'environnement
├── README.md                   # Documentation du projet
├── requirements.txt            # Dépendances du projet
└── run.py                      # Script pour démarrer l'application
```

## Description des composants principaux

### Fichiers racine
- **run.py**: Script de démarrage du serveur
- **.env**: Configuration des variables d'environnement (non versionné)
- **.env.example**: Exemple de configuration des variables d'environnement
- **requirements.txt**: Liste des dépendances Python

### Package app
- **main.py**: Configure et initialise l'application FastAPI

### Sous-package api
- **bluetooth.py**: Endpoints pour les opérations de scan Bluetooth
- **session.py**: Endpoints pour la gestion des sessions MCP

### Sous-package models
- **bluetooth.py**: Modèles Pydantic pour les données Bluetooth
- **session.py**: Modèles Pydantic pour les sessions

### Sous-package services
- **bluetooth_service.py**: Logique métier pour les opérations Bluetooth

### Sous-package core
- **config.py**: Configuration centrale de l'application

### Sous-package utils
- Utilitaires et fonctions d'aide diverses
`,
  `file_path`: `structure.md`
}
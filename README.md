# Serveur MCP Bluetooth

Ce projet est un serveur ModelContextProtocol (MCP) qui permet à Claude AI de détecter les appareils Bluetooth à proximité. Implémenté selon la méthodologie TDD (Test-Driven Development), il offre une interface robuste et testée pour l'interaction avec les périphériques Bluetooth.

## Fonctionnalités

- Scanner les appareils Bluetooth à proximité (BLE et Classic)
- Filtrer les appareils par nom
- Détecter automatiquement les appareils spéciaux (Freebox, TV, etc.)
- Obtenir des informations détaillées sur les appareils (fabricant, type, etc.)
- Support multiplateforme (Windows, Linux, macOS)
- Optimisations spécifiques pour Windows
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

Créer et activer un environnement virtuel :
bashCopier# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate

Installer les dépendances :
bashCopierpip install -r requirements.txt

Configurer les variables d'environnement :
bashCopier# Copier le fichier d'exemple
cp .env.example .env

# Éditer selon vos besoins
nano .env


Démarrage du serveur
API Bluetooth
bashCopier# Méthode simple
python run.py

# Alternative avec uvicorn directement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Serveur MCP
bashCopier# Démarrer le serveur MCP
python bluetooth_mcp_server.py
Utilisation avec Claude

Exposer le serveur à Internet via ngrok ou un déploiement sur un serveur :
bashCopierngrok http 8000

Configurer le MCP dans Claude :
bashCopiernpx @anthropic-ai/sdk install-model-context-protocol <URL_DU_SERVEUR>

Une fois configuré, vous pouvez demander à Claude d'utiliser l'outil Bluetooth :
CopierPeux-tu scanner les appareils Bluetooth à proximité ?


Tests
Ce projet est développé suivant l'approche TDD (Test-Driven Development). Pour exécuter les tests :
bashCopier# Exécuter tous les tests
pytest

# Exécuter des tests spécifiques
pytest tests/api/  # Tests des API
pytest tests/models/  # Tests des modèles
pytest tests/services/  # Tests des services
Structure du projet
Le projet suit une architecture modulaire avec séparation claire des responsabilités :

app/ : Application principale

api/ : Endpoints FastAPI
models/ : Modèles de données
services/ : Logique métier
utils/ : Fonctions utilitaires
data/ : Données statiques (identifiants Bluetooth, etc.)


mcp_sdk/ : SDK pour intégration MCP
tests/ : Tests unitaires et d'intégration

Pour une description détaillée, voir architecture.md.
Fonctionnement

API Bluetooth : Fournit des endpoints REST pour scanner les appareils Bluetooth
Serveur MCP : Implémente le protocole MCP pour permettre à Claude d'utiliser l'API Bluetooth
SDK MCP : Permet d'intégrer l'outil Bluetooth dans d'autres applications compatibles MCP

Dépannage
Problèmes Bluetooth

Erreur "Access denied" : Exécutez le serveur avec des privilèges administrateur ou sudo
Adaptateur non détecté : Vérifiez que le Bluetooth est activé dans les paramètres de votre système
Scan ne trouve aucun appareil : Assurez-vous que des appareils Bluetooth à proximité sont en mode découvrable
Problèmes sur Windows : Vérifiez que les services Bluetooth sont activés (services.msc)

Problèmes MCP

Claude ne détecte pas l'outil : Vérifiez que l'URL du serveur MCP est correcte et accessible
Erreurs d'exécution : Consultez les logs du serveur pour plus de détails

Contribuer
Les contributions sont les bienvenues ! Veuillez suivre ces étapes :

Forker le projet
Créer une branche (git checkout -b feature/amazing-feature)
Écrire des tests pour votre fonctionnalité
Implémenter votre fonctionnalité
Vérifier que tous les tests passent
Committer vos changements (git commit -m 'Add amazing feature')
Pousser vers la branche (git push origin feature/amazing-feature)
Ouvrir une Pull Request

Licence
MIT
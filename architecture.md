# Bluetooth MCP Server Architecture

<div align="center">

![Architecture](https://img.shields.io/badge/Architecture-Document-blue?style=for-the-badge)

**Detailed architectural overview of the Bluetooth MCP Server project**

</div>

## 📋 Overview

This document outlines the architectural structure of the Bluetooth MCP Server project, which enables AI assistants to discover and interact with Bluetooth devices. The architecture follows a modular design with clear separation of concerns, adhering to best practices for Python applications.

## 🏗️ Project Structure

```
bluetooth-mcp-server/            # Root project directory
│
├── app/                         # Main application package
│   ├── __init__.py              # Package initializer
│   ├── main.py                  # FastAPI application entry point
│   │
│   ├── api/                     # API endpoints package
│   │   ├── __init__.py          # Package initializer
│   │   ├── bluetooth.py         # Bluetooth operation endpoints
│   │   └── session.py           # MCP session management endpoints
│   │
│   ├── core/                    # Core configuration package
│   │   ├── __init__.py          # Package initializer
│   │   └── config.py            # Application configuration
│   │
│   ├── data/                    # Static data package
│   │   ├── __init__.py          # Package initializer
│   │   ├── company_identifiers.py  # Bluetooth manufacturer IDs database
│   │   └── mac_prefixes.py      # MAC address prefix database
│   │
│   ├── models/                  # Data models package
│   │   ├── __init__.py          # Package initializer
│   │   ├── bluetooth.py         # Bluetooth data models
│   │   └── session.py           # Session data models
│   │
│   ├── services/                # Business logic package
│   │   ├── __init__.py          # Package initializer
│   │   ├── bluetooth_service.py # Main Bluetooth operations service
│   │   ├── ble_scanner.py       # BLE scanning service
│   │   ├── classic_scanner.py   # Classic Bluetooth scanning service
│   │   ├── windows_scanner.py   # Windows-specific scanner
│   │   └── windows_advanced_scanner.py # Enhanced Windows scanner
│   │
│   └── utils/                   # Utilities package
│       ├── __init__.py          # Package initializer
│       └── bluetooth_utils.py   # Bluetooth utility functions
│
├── mcp_sdk/                     # MCP SDK package
│   ├── __init__.py              # Package initializer
│   ├── bluetooth_tool.py        # MCP Bluetooth tool implementation
│   ├── setup.py                 # Package installation configuration
│   └── tests/                   # SDK tests
│       ├── __init__.py          # Package initializer
│       └── test_bluetooth_tool.py # Bluetooth tool tests
│
├── tests/                       # Test suites
│   ├── __init__.py              # Package initializer
│   ├── test_main.py             # Main application tests
│   ├── TEST.md                  # Test status documentation
│   │
│   ├── api/                     # API tests package
│   │   ├── __init__.py          # Package initializer
│   │   ├── test_bluetooth.py    # Bluetooth API tests
│   │   └── test_session.py      # Session API tests
│   │
│   ├── models/                  # Model tests package
│   │   ├── __init__.py          # Package initializer
│   │   ├── test_bluetooth_model.py # Bluetooth model tests
│   │   └── test_session_model.py # Session model tests
│   │
│   ├── services/                # Service tests package
│   │   ├── __init__.py          # Package initializer
│   │   ├── test_bluetooth_service.py # Bluetooth service tests
│   │   └── test_classic_bluetooth.py # Classic Bluetooth tests
│   │
│   └── utils/                   # Utility tests package
│       ├── __init__.py          # Package initializer
│       └── test_bluetooth_utils.py # Bluetooth utilities tests
│
├── .env                         # Local environment variables
├── .env.example                 # Environment variables example
├── run.py                       # Application startup script
├── bluetooth_mcp_server.py      # MCP server startup script
├── requirements.txt             # Project dependencies
├── architecture.md              # This architecture document
└── README.md                    # Project documentation
```

## 🧩 Component Descriptions

### 🔄 Core Components

#### `run.py`
Entry point script for starting the FastAPI server, using environment variables for configuration.

#### `bluetooth_mcp_server.py`
Entry point script for the MCP server that integrates with the Bluetooth API.

#### `app/main.py`
Configures and initializes the FastAPI application, sets up CORS, and includes routers.

### 🌐 API Layer (`app/api/`)

#### `bluetooth.py`
Provides REST endpoints for Bluetooth scanning operations:
- POST `/mcp/v1/tools/bluetooth-scan`: Standard Bluetooth scan
- POST `/mcp/v1/tools/bluetooth-scan-fast`: Optimized for speed
- POST `/mcp/v1/tools/bluetooth-scan-thorough`: Optimized for device discovery

#### `session.py`
Handles MCP session management:
- POST `/mcp/v1/session`: Creates a new MCP session and returns available tools

### 📊 Data Models (`app/models/`)

#### `bluetooth.py`
Pydantic models for Bluetooth data:
- `BluetoothDevice`: Represents a discovered Bluetooth device
- `BluetoothScanParams`: Parameters for scan operations
- `ScanResponse`: Container for scan results

#### `session.py`
Models for MCP session handling:
- `SessionResponse`: Represents the MCP session response
- `bluetooth_scan_tool`: Defines the Bluetooth tool for MCP

### 🔧 Services (`app/services/`)

#### `bluetooth_service.py`
Orchestrates the different Bluetooth scanners and manages device data:
- Handles device deduplication
- Merges information from different scan sources
- Provides platform-specific optimizations

#### `ble_scanner.py`
BLE-specific scanning service using Bleak library.

#### `classic_scanner.py`
Classic Bluetooth scanning service, with fallback modes for different platforms.

#### `windows_scanner.py`
Windows-specific scanner using native Windows APIs.

#### `windows_advanced_scanner.py`
Enhanced Windows scanner for detecting special devices (TVs, Freebox, etc.).

### 🛠️ Utilities (`app/utils/`)

#### `bluetooth_utils.py`
Helper functions for Bluetooth operations:
- MAC address normalization
- Manufacturer data formatting
- Device name deduction
- Device information merging

### 📚 Static Data (`app/data/`)

#### `company_identifiers.py`
Database of Bluetooth manufacturer identifiers.

#### `mac_prefixes.py`
Database of MAC address prefixes for device identification.

### 🔌 MCP SDK (`mcp_sdk/`)

#### `bluetooth_tool.py`
Implementation of the Bluetooth tool for the MCP protocol.

### 🧪 Tests (`tests/`)

Test suites following the same structure as the application code, adhering to Test-Driven Development principles.

## 🔄 Data Flow

1. **Client Request** → The MCP client (Claude) sends a tool execution request
2. **MCP Server** → Processes the request and calls the appropriate Bluetooth API endpoint
3. **API Endpoint** → Validates parameters and calls the Bluetooth service
4. **Bluetooth Service** → Orchestrates the appropriate scanners based on parameters
5. **Scanners** → Execute device discovery using platform-specific methods
6. **Device Processing** → Discovered devices are processed, deduplicated, and enhanced
7. **Response** → Results are returned through the service → API → MCP chain

## 🔒 Configuration Management

The application uses a hierarchical configuration approach:

1. **Default values** hardcoded in the application
2. **.env file** for environment-specific configuration
3. **Environment variables** that can override file settings
4. **Runtime parameters** passed to API endpoints

## 🔄 Dependency Injection

The project uses a simple form of dependency injection:

- Services are instantiated as singletons
- API endpoints access services through imports
- Test mocks replace real implementations for testing

## 🧩 Extension Points

The architecture is designed to be extendable:

1. **Adding new scan methods**: Implement a new scanner in `app/services/`
2. **Supporting new device types**: Extend the databases in `app/data/`
3. **Adding new MCP tools**: Implement new tools in `mcp_sdk/`
4. **Enhanced device information**: Extend the `BluetoothDevice` model

## 📈 Performance Considerations

- **Parallel scanning**: Multiple scan methods run concurrently
- **Scan duration control**: Adjustable to balance speed vs. thoroughness
- **Device deduplication**: Optimizes result size and clarity
- **Platform-specific optimizations**: Maximizes performance on each OS

## 🔐 Security Considerations

- **Limited scope**: The server only performs Bluetooth scanning operations
- **Input validation**: All parameters are validated using Pydantic models
- **Error handling**: Proper exception handling prevents information leakage
- **No persistent storage**: No sensitive data is stored between requests

## 🔄 Testing Strategy

The project follows a Test-Driven Development (TDD) approach:

1. **Unit Tests**: For individual components (models, utilities)
2. **Integration Tests**: For service interactions
3. **API Tests**: For endpoint behavior
4. **Mocking**: External dependencies are mocked for reliable testing
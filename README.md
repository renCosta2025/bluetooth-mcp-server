# Bluetooth MCP Server

<div align="center">

![Bluetooth Logo](https://img.shields.io/badge/Bluetooth-MCP-blue?style=for-the-badge&logo=bluetooth&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0%2B-green)](https://fastapi.tiangolo.com/)
[![TDD](https://img.shields.io/badge/TDD-Driven-red)](https://en.wikipedia.org/wiki/Test-driven_development)

**Model Context Protocol Server for Bluetooth Device Detection**

</div>

## 🔍 Overview

This project implements a Model Context Protocol (MCP) server that enables Claude and other AI assistants to scan and interact with Bluetooth devices in your vicinity. Built with a Test-Driven Development approach, it provides a robust, tested interface for Bluetooth operations across multiple platforms.

## ✨ Features

- 📡 **Multi-protocol scanning**: Detect both BLE and Classic Bluetooth devices
- 🔎 **Flexible filtering**: Filter devices by name, type, or other attributes
- 🔄 **Automatic device recognition**: Identify and categorize common devices (like Freebox, TVs, etc.)
- 📱 **Enhanced device information**: Get manufacturer info, device type, and detailed characteristics
- 🖥️ **Cross-platform support**: Works on Windows, macOS, and Linux
- ⚡ **Platform-specific optimizations**: Enhanced detection capabilities on Windows
- 🤖 **MCP Integration**: Seamless integration with Claude and compatible AI assistants

## 📋 Requirements

- **Python 3.7+**
- **Bluetooth adapter** (built-in or external)
- **Admin/sudo privileges** (required for some Bluetooth operations)
- **Internet connection** (for package installation)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bluetooth-mcp-server.git
cd bluetooth-mcp-server

# Create and activate virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit the .env file as needed
```

### Running the Server

```bash
# Start the Bluetooth API server
python run.py

# In another terminal, start the MCP server
python bluetooth_mcp_server.py
```

### Using with Claude

1. Expose your server to the internet using ngrok or deploy it to a server:
   ```bash
   ngrok http 8000
   ```

2. Configure Claude to use your MCP server:
   ```bash
   npx @anthropic-ai/sdk install-model-context-protocol <YOUR_SERVER_URL>
   ```

3. Ask Claude to scan for Bluetooth devices:
   ```
   Could you scan for nearby Bluetooth devices?
   ```

## 🧪 Testing

This project follows a Test-Driven Development (TDD) approach with comprehensive test coverage:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/api/       # API tests
pytest tests/models/    # Data model tests
pytest tests/services/  # Service logic tests
pytest tests/utils/     # Utility function tests
```

## 🏗️ Architecture

The project follows a modular architecture with clear separation of concerns:

```
bluetooth-mcp-server/
├── app/                # Main application package
│   ├── api/            # FastAPI endpoints
│   ├── core/           # Core configuration
│   ├── data/           # Static data (Bluetooth identifiers, etc.)
│   ├── models/         # Data models
│   ├── services/       # Business logic
│   └── utils/          # Utility functions
├── mcp_sdk/            # MCP integration SDK
└── tests/              # Test suites
```

For detailed architecture information, see [architecture.md](architecture.md).

## 🔧 Troubleshooting

### Bluetooth Issues

- **"Access denied" errors**: Run the server with admin/sudo privileges
- **Adapter not detected**: Ensure Bluetooth is enabled in your system settings
- **No devices found**: Make sure there are discoverable Bluetooth devices nearby
- **Windows-specific issues**: Check that Bluetooth services are active (`services.msc`)

### MCP Issues

- **Tool not detected by Claude**: Verify your MCP server URL is correct and accessible
- **Execution errors**: Check the server logs for detailed error information

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your feature
4. Implement your feature
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Bleak](https://github.com/hbldh/bleak) for cross-platform Bluetooth functionality
- [Anthropic Claude](https://www.anthropic.com/claude) for MCP integration support
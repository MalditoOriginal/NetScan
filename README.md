# IP Definition Project

A comprehensive, modular IP address analysis tool supporting IPv4, IPv6, network calculations, and more.

## Architecture

```
ip_project/
├── core/              # Core IP logic (Abstract, IPv4, IPv6, validators, network)
│   ├── __init__.py
│   ├── ip_address.py  # IP address classes with factory pattern
│   ├── network.py     # Network calculations and subnetting
│   └── validators.py  # IP validation functions
│
├── services/          # External services (PublicIPDetector, DNSResolver)
│   ├── __init__.py
│   ├── public_ip.py   # Public IP detection from multiple services
│   └── resolution.py  # DNS resolution with caching
│
├── gui/               # GUI components (base, views, controllers)
│   ├── __init__.py
│   ├── base.py        # Base GUI class with observer pattern
│   ├── Views/         # View components
│   │   ├── __init__.py
│   │   ├── ip_input.py  # IP input view
│   │   ├── results.py   # Results display view
│   │   └── examples.py  # Examples viewer
│   └── Controllers/   # UI controllers
│       ├── __init__.py
│       └── main.py      # Main window controller
│
├── utils/             # Utilities (config, logger)
│   ├── __init__.py
│   ├── config.py      # Configuration management
│   └── logger.py      # Logging configuration
│
├── tests/             # Test files
│   ├── __init__.py
│   ├── test_core/
│   ├── test_services/
│   ├── test_gui/
│   └── test_utils/
│
├── main.py            # Main entry point (CLI, GUI, API)
├── requirements.txt
└── README.md          # This file
```

## Features

- **IPv4/IPv6 Analysis**: Full address validation, classification, and information
- **Network Calculations**: Subnetting, CIDR notation, host ranges
- **Public IP Detection**: Multiple fallback services for external IP discovery
- **DNS Resolution**: Caching, async resolution, reverse lookups
- **Modern GUI**: ttkbootstrap theming with observer pattern
- **Multiple Interfaces**: CLI, GUI, and REST API

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ip_project

# Install dependencies
pip install -r requirements.txt

# Optional: Install for development
pip install -e .
```

## Usage

### GUI Mode (Default)
```bash
python -m ip_project.main
```

### CLI Mode
```bash
# Show public IP
python -m ip_project.main cli --public

# Show local IP
python -m ip_project.main cli --local

# Analyze an IP
python -m ip_project.main cli 8.8.8.8

# Verbose mode
python -m ip_project.main cli 192.168.1.1 --verbose
```

### API Mode
```bash
# Start API server on http://localhost:5000
python -m ip_project.main api

# API endpoints:
# GET  /api/health
# GET  /api/analyze/<ip_address>
# GET  /api/public-ip
```

## Running Tests

```bash
# Install test dependencies
pip install pytest coverage

# Run all tests
pytest tests/

# Run with coverage
coverage run -m pytest tests/
coverage report

# Run specific test module
pytest tests/test_core/test_ip_address.py
```

## Extension Guide

### Adding a New Service

1. Create a new file in `ip_project/services/`
2. Import the class in `ip_project/services/__init__.py`
3. Follow the existing pattern with logging and config support

### Adding a New View

1. Create a new file in `ip_project/gui/Views/`
2. Implement the view as a ttk.Frame
3. Import in `ip_project/gui/Views/__init__.py`
4. Use the observer pattern for updates

### Adding a New Controller

1. Create a new file in `ip_project/gui/Controllers/`
2. Implement the controller logic
3. Import in `ip_project/gui/Controllers/__init__.py`
4. Connect to views via observer pattern

## Configuration

Configuration is managed through `ConfigManager` and stored in JSON format:

```json
{
  "ui": {
    "theme": "dark",
    "window_size": {"width": 800, "height": 600}
  },
  "ip_services": {
    "ipify": {"url": "https://api.ipify.org", "enabled": true}
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run existing tests: `pytest tests/`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Uses Python's built-in `ipaddress` module
- Public IP detection services: ipify, ipinfo, ifconfig.me
- GUI built with ttkbootstrap

"""
Configuration management module.

This module provides a configuration manager with support for
loading, saving, and managing application configuration.
"""

import json
import os
import threading
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """
    Manager for application configuration.
    
    Supports loading configuration from JSON files,
    dynamic configuration changes, and default values.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self._config: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._config_file = config_file
        
        # Set default configuration
        self._set_defaults()
        
        # Load from file if specified
        if config_file:
            self.load(config_file)
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self._defaults = {
            "ui": {
                "theme": "dark",
                "window_size": {"width": 800, "height": 600},
                "show_toolbar": True,
                "show_statusbar": True,
            },
            "ip_services": {
                "ipify": {
                    "url": "https://api.ipify.org",
                    "timeout": 10,
                    "enabled": True,
                },
                "ipinfo": {
                    "url": "https://ipinfo.io/ip",
                    "timeout": 10,
                    "enabled": True,
                },
                "ifconfig": {
                    "url": "https://ifconfig.me/ip",
                    "timeout": 10,
                    "enabled": True,
                },
            },
            "dns_resolver": {
                "enable_cache": True,
                "default_ttl": 300,
            },
            "logging": {
                "level": "INFO",
                "file": "logs/ip_project.log",
            },
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (use dot notation for nested values)
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        with self._lock:
            parts = key.split(".")
            value = self._config
            
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    # Try defaults
                    value = self._defaults
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            return default
            
            return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (use dot notation for nested values)
            value: Value to set
        """
        with self._lock:
            parts = key.split(".")
            config = self._config
            
            # Navigate to the nested dictionary
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            
            # Set the value
            config[parts[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        with self._lock:
            return self._config.copy()
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get all default configuration values."""
        return self._defaults.copy()
    
    def merge(self, config: Dict[str, Any]) -> None:
        """
        Merge config values into existing configuration.
        
        Args:
            config: Configuration dictionary to merge
        """
        with self._lock:
            self._merge_dict(self._config, config)
    
    def _merge_dict(self, target: Dict, source: Dict) -> None:
        """Recursively merge source into target."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dict(target[key], value)
            else:
                target[key] = value
    
    def load(self, file_path: str) -> bool:
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            with self._lock:
                self._config = config
            
            self._config_file = file_path
            return True
        except (IOError, json.JSONDecodeError) as e:
            return False
    
    def save(self, file_path: Optional[str] = None) -> bool:
        """
        Save configuration to a JSON file.
        
        Args:
            file_path: Path to save configuration (uses configured path if None)
            
        Returns:
            True if successful, False otherwise
        """
        path = file_path or self._config_file
        if not path:
            return False
        
        try:
            # Create directory if needed
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            
            return True
        except IOError as e:
            return False
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        with self._lock:
            self._config = {}
    
    def reset_key(self, key: str) -> None:
        """Reset a specific configuration key to default."""
        with self._lock:
            # Remove from config
            parts = key.split(".")
            config = self._config
            
            for part in parts[:-1]:
                if isinstance(config, dict) and part in config:
                    config = config[part]
                else:
                    return
            
            if isinstance(config, dict) and parts[-1] in config:
                del config[parts[-1]]

"""
Public IP detection module.

This module provides functionality to detect the public IP address
by querying multiple configurable IP detection services.
"""

import urllib.request
import urllib.error
import socket
import threading
from typing import List, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from ip_project.utils.logger import get_logger
from ip_project.utils.config import ConfigManager


@dataclass
class IPService:
    """Configuration for an IP detection service."""
    name: str
    url: str
    timeout: int = 10
    enabled: bool = True
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, IPService):
            return self.name == other.name
        return NotImplemented


class PublicIPDetector:
    """
    Detects the public IP address by querying multiple services.
    
    Supports configurable IP detection services with fallback
    and parallel querying for improved performance.
    """
    
    # Default IP detection services
    DEFAULT_SERVICES = [
        IPService("ipify", "https://api.ipify.org", timeout=10),
        IPService("ipinfo", "https://ipinfo.io/ip", timeout=10),
        IPService("ifconfig", "https://ifconfig.me/ip", timeout=10),
        IPService("icanhazip", "https://icanhazip.com", timeout=10),
    ]
    
    def __init__(self, services: Optional[List[IPService]] = None):
        """
        Initialize the PublicIPDetector.
        
        Args:
            services: List of IP detection services. Uses defaults if None.
        """
        self._logger = get_logger(self.__class__.__name__)
        self._services = services if services is not None else self.DEFAULT_SERVICES.copy()
        self._last_used_service = None
        self._config = ConfigManager()
        
        # Load services from config if available
        self._load_services_from_config()
    
    def _load_services_from_config(self) -> None:
        """Load services configuration from config manager."""
        try:
            service_configs = self._config.get("ip_services", {})
            for name, config in service_configs.items():
                if isinstance(config, dict):
                    service = IPService(
                        name=name,
                        url=config.get("url", ""),
                        timeout=config.get("timeout", 10),
                        enabled=config.get("enabled", True),
                    )
                    self._update_service(service)
        except Exception as e:
            self._logger.warning(f"Failed to load services from config: {e}")
    
    def _update_service(self, service: IPService) -> None:
        """Update or add a service."""
        for i, existing in enumerate(self._services):
            if existing.name == service.name:
                self._services[i] = service
                return
        self._services.append(service)
    
    def add_service(self, name: str, url: str, timeout: int = 10, enabled: bool = True) -> None:
        """
        Add a new IP detection service.
        
        Args:
            name: Service name
            url: URL to query for IP detection
            timeout: Request timeout in seconds
            enabled: Whether the service is enabled
        """
        service = IPService(name=name, url=url, timeout=timeout, enabled=enabled)
        self._update_service(service)
        self._logger.info(f"Added IP detection service: {name}")
    
    def remove_service(self, name: str) -> bool:
        """
        Remove an IP detection service.
        
        Args:
            name: Name of the service to remove
            
        Returns:
            True if service was removed, False if not found
        """
        for i, service in enumerate(self._services):
            if service.name == name:
                self._services.pop(i)
                self._logger.info(f"Removed IP detection service: {name}")
                return True
        self._logger.warning(f"Service not found: {name}")
        return False
    
    def enable_service(self, name: str) -> bool:
        """Enable a service by name."""
        return self._set_service_enabled(name, True)
    
    def disable_service(self, name: str) -> bool:
        """Disable a service by name."""
        return self._set_service_enabled(name, False)
    
    def _set_service_enabled(self, name: str, enabled: bool) -> bool:
        """Set service enabled state."""
        for service in self._services:
            if service.name == name:
                service.enabled = enabled
                status = "enabled" if enabled else "disabled"
                self._logger.info(f"Service {name} {status}")
                return True
        return False
    
    def get_available_services(self) -> List[IPService]:
        """Get list of all configured services."""
        return self._services.copy()
    
    def detect_public_ip(self, timeout: int = 10, max_workers: int = 3) -> Optional[str]:
        """
        Detect the public IP address by querying services.
        
        Uses parallel queries with a timeout and returns the first
        successful response.
        
        Args:
            timeout: Per-request timeout in seconds
            max_workers: Maximum number of parallel workers
            
        Returns:
            Public IP address string or None if all services fail
        """
        self._logger.info("Starting public IP detection")
        
        # Filter enabled services
        enabled_services = [s for s in self._services if s.enabled]
        
        if not enabled_services:
            self._logger.warning("No enabled IP detection services")
            return None
        
        results = {}
        errors = {}
        
        def query_service(service: IPService) -> tuple:
            """Query a single service and return (service_name, ip, error)."""
            try:
                url = service.url
                self._logger.debug(f"Querying service: {service.name} at {url}")
                
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "IP-Definition-Client/1.0"}
                )
                
                with urllib.request.urlopen(request, timeout=service.timeout) as response:
                    ip = response.read().decode('utf-8').strip()
                    self._logger.debug(f"Service {service.name} returned: {ip}")
                    return (service.name, ip, None)
                    
            except urllib.error.URLError as e:
                error = f"URL error: {e.reason}"
                self._logger.error(f"Service {service.name} failed: {error}")
                return (service.name, None, error)
            except urllib.error.HTTPError as e:
                error = f"HTTP error {e.code}: {e.reason}"
                self._logger.error(f"Service {service.name} failed: {error}")
                return (service.name, None, error)
            except socket.timeout as e:
                error = f"Timeout: {e}"
                self._logger.error(f"Service {service.name} timed out: {e}")
                return (service.name, None, error)
            except Exception as e:
                error = f"Unexpected error: {e}"
                self._logger.error(f"Service {service.name} failed with: {e}")
                return (service.name, None, error)
        
        # Query services in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_service = {
                executor.submit(query_service, service): service.name
                for service in enabled_services
            }
            
            for future in as_completed(future_to_service, timeout=timeout):
                service_name, ip, error = future.result()
                if ip:
                    self._last_used_service = service_name
                    self._logger.info(f"Successfully detected IP: {ip} via {service_name}")
                    return ip
                else:
                    errors[service_name] = error
        
        # All services failed
        self._logger.error(f"IP detection failed: {errors}")
        return None
    
    def detect_public_ip_sync(self, timeout: int = 10) -> Optional[str]:
        """
        Detect the public IP address synchronously.
        
        Queries services sequentially until one succeeds.
        
        Args:
            timeout: Per-request timeout in seconds
            
        Returns:
            Public IP address string or None if all services fail
        """
        self._logger.info("Starting synchronous public IP detection")
        
        for service in self._services:
            if not service.enabled:
                continue
                
            try:
                url = service.url
                self._logger.debug(f"Querying service: {service.name} at {url}")
                
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "IP-Definition-Client/1.0"}
                )
                
                with urllib.request.urlopen(request, timeout=min(service.timeout, timeout)) as response:
                    ip = response.read().decode('utf-8').strip()
                    self._last_used_service = service_name
                    self._logger.info(f"Successfully detected IP: {ip} via {service.name}")
                    return ip
                    
            except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout) as e:
                self._logger.warning(f"Service {service.name} failed: {e}")
                continue
            except Exception as e:
                self._logger.error(f"Service {service.name} failed with: {e}")
                continue
        
        self._logger.error("IP detection failed: All services failed")
        return None
    
    def get_last_used_service(self) -> Optional[str]:
        """Get the name of the last successful service."""
        return self._last_used_service
    
    def test_service(self, name: str) -> tuple:
        """
        Test a specific IP detection service.
        
        Args:
            name: Name of the service to test
            
        Returns:
            Tuple of (success: bool, ip: Optional[str], error: Optional[str])
        """
        for service in self._services:
            if service.name == name:
                _, ip, error = query_service(service)
                return (ip is not None, ip, error)
        
        self._logger.warning(f"Service not found: {name}")
        return (False, None, "Service not found")
    
    def refresh_services(self) -> None:
        """Refresh services from configuration."""
        self._services = self.DEFAULT_SERVICES.copy()
        self._load_services_from_config()
        self._logger.info("Services refreshed from configuration")
    
    def save_services_to_config(self) -> None:
        """Save current services configuration to config manager."""
        service_configs = {}
        for service in self._services:
            service_configs[service.name] = {
                "url": service.url,
                "timeout": service.timeout,
                "enabled": service.enabled,
            }
        self._config.set("ip_services", service_configs)
        self._logger.info("Services saved to configuration")

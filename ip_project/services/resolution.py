"""
DNS and hostname resolution module.

This module provides DNS resolution functionality for hostnames
and IP addresses with caching and asynchronous support.
"""

import socket
import threading
from typing import List, Optional, Dict
from dataclasses import dataclass
from time import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from ip_project.utils.logger import get_logger
from ip_project.utils.config import ConfigManager


@dataclass
class DNSRecord:
    """Container for DNS record information."""
    hostname: str
    ip_address: str
    aliases: List[str]
    record_type: str
    timestamp: float
    
    def is_expired(self, ttl: int = 300) -> bool:
        """Check if the record has expired."""
        return (time() - self.timestamp) > ttl


class DNSResolver:
    """
    DNS resolver with caching and parallel resolution support.
    
    Supports both IPv4 and IPv6 resolution with optional
    caching for improved performance.
    """
    
    def __init__(self, enable_cache: bool = True, default_ttl: int = 300):
        """
        Initialize the DNSResolver.
        
        Args:
            enable_cache: Whether to enable caching
            default_ttl: Default cache TTL in seconds
        """
        self._logger = get_logger(self.__class__.__name__)
        self._enable_cache = enable_cache
        self._default_ttl = default_ttl
        self._cache: Dict[str, DNSRecord] = {}
        self._cache_lock = threading.Lock()
        self._config = ConfigManager()
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load DNS resolver configuration."""
        try:
            cache_config = self._config.get("dns_resolver", {})
            self._enable_cache = cache_config.get("enable_cache", self._enable_cache)
            self._default_ttl = cache_config.get("default_ttl", self._default_ttl)
            self._logger.info(f"Loaded DNS config: cache={self._enable_cache}, ttl={self._default_ttl}")
        except Exception as e:
            self._logger.warning(f"Failed to load DNS config: {e}")
    
    def resolve(self, hostname: str, family: int = socket.AF_UNSPEC) -> Optional[str]:
        """
        Resolve a hostname to an IP address.
        
        Args:
            hostname: Hostname to resolve
            family: Address family (AF_UNSPEC, AF_INET, AF_INET6)
            
        Returns:
            IP address string or None if resolution fails
        """
        self._logger.debug(f"Resolving hostname: {hostname}")
        
        # Check cache first
        if self._enable_cache:
            cached = self._get_from_cache(hostname)
            if cached:
                self._logger.debug(f"Cache hit for {hostname}: {cached.ip_address}")
                return cached.ip_address
        
        try:
            # Resolve the hostname
            info = socket.getaddrinfo(
                hostname,
                None,
                family=family,
                type=socket.SOCK_STREAM
            )
            
            # Extract IP addresses
            ip_addresses = [item[4][0] for item in info]
            
            # Get the first non-localhost address if available
            ip_address = ip_addresses[0] if ip_addresses else None
            
            # Store in cache
            if ip_address and self._enable_cache:
                self._store_in_cache(hostname, ip_address, [item[0].name for item in info])
            
            self._logger.info(f"Resolved {hostname} to {ip_address}")
            return ip_address
            
        except socket.gaierror as e:
            self._logger.error(f"DNS resolution failed for {hostname}: {e}")
            return None
        except Exception as e:
            self._logger.error(f"Unexpected error resolving {hostname}: {e}")
            return None
    
    def resolve_async(self, hostname: str, family: int = socket.AF_UNSPEC) -> Optional[str]:
        """
        Resolve a hostname asynchronously.
        
        Args:
            hostname: Hostname to resolve
            family: Address family
            
        Returns:
            IP address string or None if resolution fails
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.resolve, hostname, family)
            return future.result()
    
    def resolve_all(self, hostname: str, family: int = socket.AF_UNSPEC) -> List[str]:
        """
        Resolve a hostname to all available IP addresses.
        
        Args:
            hostname: Hostname to resolve
            family: Address family
            
        Returns:
            List of IP address strings
        """
        self._logger.debug(f" Resolving all addresses for: {hostname}")
        
        # Check cache first
        if self._enable_cache:
            cached = self._get_from_cache(hostname)
            if cached:
                return [cached.ip_address]
        
        try:
            info = socket.getaddrinfo(
                hostname,
                None,
                family=family,
                type=socket.SOCK_STREAM
            )
            
            ip_addresses = []
            for item in info:
                ip = item[4][0]
                if ip not in ip_addresses:
                    ip_addresses.append(ip)
            
            # Store in cache
            if ip_addresses and self._enable_cache:
                self._store_in_cache(hostname, ip_addresses[0], [item[0].name for item in info])
            
            self._logger.info(f"Resolved {hostname} to {ip_addresses}")
            return ip_addresses
            
        except socket.gaierror as e:
            self._logger.error(f"DNS resolution failed for {hostname}: {e}")
            return []
        except Exception as e:
            self._logger.error(f"Unexpected error resolving {hostname}: {e}")
            return []
    
    def reverse_resolve(self, ip_address: str) -> Optional[str]:
        """
        Perform reverse DNS lookup.
        
        Args:
            ip_address: IP address to resolve
            
        Returns:
            Hostname string or None if resolution fails
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            self._logger.info(f"Reverse resolved {ip_address} to {hostname}")
            return hostname
        except socket.herror as e:
            self._logger.error(f"Reverse DNS resolution failed for {ip_address}: {e}")
            return None
        except Exception as e:
            self._logger.error(f"Unexpected error reverse resolving {ip_address}: {e}")
            return None
    
    def batch_resolve(self, hostnames: List[str], family: int = socket.AF_UNSPEC, 
                      max_workers: int = 5) -> Dict[str, Optional[str]]:
        """
        Resolve multiple hostnames in parallel.
        
        Args:
            hostnames: List of hostnames to resolve
            family: Address family
            max_workers: Maximum number of parallel workers
            
        Returns:
            Dictionary mapping hostname to IP address
        """
        results = {}
        
        def resolve_single(hostname: str) -> tuple:
            """Resolve a single hostname."""
            return (hostname, self.resolve(hostname, family))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_hostname = {
                executor.submit(resolve_single, hostname): hostname
                for hostname in hostnames
            }
            
            for future in as_completed(future_to_hostname):
                hostname, ip = future.result()
                results[hostname] = ip
        
        self._logger.info(f"Batch resolved {len(hostnames)} hostnames")
        return results
    
    def _get_from_cache(self, hostname: str) -> Optional[DNSRecord]:
        """Get a record from cache if not expired."""
        if not self._enable_cache:
            return None
        
        with self._cache_lock:
            record = self._cache.get(hostname)
            if record and not record.is_expired(self._default_ttl):
                return record
            elif record:
                del self._cache[hostname]
            return None
    
    def _store_in_cache(self, hostname: str, ip_address: str, aliases: List[str]) -> None:
        """Store a record in cache."""
        if not self._enable_cache:
            return
        
        with self._cache_lock:
            record = DNSRecord(
                hostname=hostname,
                ip_address=ip_address,
                aliases=aliases,
                record_type="A",
                timestamp=time()
            )
            self._cache[hostname] = record
    
    def clear_cache(self) -> None:
        """Clear all cached records."""
        with self._cache_lock:
            self._cache.clear()
        self._logger.info("DNS cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        with self._cache_lock:
            return {
                "size": len(self._cache),
                "enabled": self._enable_cache,
                "default_ttl": self._default_ttl,
                "hostnames": list(self._cache.keys()),
            }
    
    def set_cache_ttl(self, ttl: int) -> None:
        """Set the default cache TTL."""
        self._default_ttl = ttl
        self._logger.info(f"Cache TTL set to {ttl} seconds")

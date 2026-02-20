"""
Network calculations and operations.

This module provides network-related functionality including
network calculations, subnetting, and host operations.
"""

import ipaddress
from dataclasses import dataclass
from typing import Optional, List, Iterator


@dataclass
class NetworkInfo:
    """Container for network information."""
    network: str
    netmask: str
    prefixlen: int
    network_address: str
    broadcast_address: str
    num_hosts: int
    first_host: Optional[str] = None
    last_host: Optional[str] = None
    version: int = 4


class NetworkCalculator:
    """Class for calculating network information."""
    
    def __init__(self, network: str = "0.0.0.0/0"):
        """
        Initialize with a network specification.
        
        Args:
            network: Network in CIDR notation (e.g., '192.168.1.0/24')
        """
        self._network = network
        self._net_obj = None
        self._parse_network(network)
    
    def _parse_network(self, network: str) -> None:
        """Parse and validate the network specification."""
        try:
            # Try IPv4 first
            self._net_obj = ipaddress.IPv4Network(network, strict=False)
            self._version = 4
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            try:
                # Try IPv6
                self._net_obj = ipaddress.IPv6Network(network, strict=False)
                self._version = 6
            except (ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
                raise ValueError(f"Invalid network specification: {network}") from e
    
    @property
    def network(self) -> str:
        """Return the network specification."""
        return self._network
    
    @property
    def network_address(self) -> str:
        """Return the network address."""
        return str(self._net_obj.network_address)
    
    @property
    def broadcast_address(self) -> str:
        """Return the broadcast address."""
        return str(self._net_obj.broadcast_address)
    
    @property
    def netmask(self) -> str:
        """Return the netmask."""
        return str(self._net_obj.netmask)
    
    @property
    def prefixlen(self) -> int:
        """Return the prefix length."""
        return self._net_obj.prefixlen
    
    @property
    def num_addresses(self) -> int:
        """Return the total number of addresses in the network."""
        return self._net_obj.num_addresses
    
    @property
    def num_hosts(self) -> int:
        """Return the number of usable host addresses."""
        return max(0, self._net_obj.num_addresses - 2)
    
    @property
    def version(self) -> int:
        """Return the IP version (4 or 6)."""
        return self._version
    
    @property
    def is_private(self) -> bool:
        """Check if the network is private."""
        return self._net_obj.is_private
    
    def first_host(self) -> Optional[str]:
        """Return the first usable host address."""
        if self.num_hosts == 0:
            return None
        return str(self._net_obj.network_address + 1)
    
    def last_host(self) -> Optional[str]:
        """Return the last usable host address."""
        if self.num_hosts == 0:
            return None
        return str(self._net_obj.broadcast_address - 1)
    
    def hosts(self) -> List[str]:
        """Return a list of all usable host addresses."""
        if self.num_hosts == 0:
            return []
        return [str(host) for host in self._net_obj.hosts()]
    
    def all_addresses(self) -> List[str]:
        """Return a list of all addresses in the network."""
        return [str(addr) for addr in self._net_obj]
    
    def contains(self, address: str) -> bool:
        """
        Check if the network contains the given address.
        
        Args:
            address: IP address to check
            
        Returns:
            True if the address is in the network, False otherwise
        """
        try:
            addr = ipaddress.ip_address(address)
            return addr in self._net_obj
        except ValueError:
            return False
    
    def subnet(self, prefixlen_diff: int = 1) -> List[str]:
        """
        Subdivide the network into subnets.
        
        Args:
            prefixlen_diff: Amount to increase the prefix length
            
        Returns:
            List of subnet strings
        """
        try:
            subnets = list(self._net_obj.subnets(prefixlen_diff=prefixlen_diff))
            return [str(subnet) for subnet in subnets]
        except ValueError as e:
            raise ValueError(f"Cannot subnet network with current prefix: {e}") from e
    
    def supernet(self, prefixlen_diff: int = 1) -> Optional[str]:
        """
        Create a supernet by combining multiple networks.
        
        Args:
            prefixlen_diff: Amount to decrease the prefix length
            
        Returns:
            Supernet string or None if not possible
        """
        try:
            supernets = list(self._net_obj.supernet(prefixlen_diff=prefixlen_diff))
            return str(supernets[0]) if supernets else None
        except ValueError as e:
            raise ValueError(f"Cannot create supernet: {e}") from e
    
    def to_info(self) -> NetworkInfo:
        """Return NetworkInfo dataclass with all network information."""
        return NetworkInfo(
            network=self._network,
            netmask=self.netmask,
            prefixlen=self.prefixlen,
            network_address=self.network_address,
            broadcast_address=self.broadcast_address,
            num_hosts=self.num_hosts,
            first_host=self.first_host(),
            last_host=self.last_host(),
            version=self.version,
        )
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"Network({self._network})"
    
    def __repr__(self) -> str:
        """Return formal string representation."""
        return f"NetworkCalculator('{self._network}')"

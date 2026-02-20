"""
IP Address classes for IPv4 and IPv6 addresses.

This module provides wrapper classes around Python's ipaddress module
with additional utility methods and a factory pattern for creation.
"""

import ipaddress
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Union, List


@dataclass
class IPInfo:
    """Container for IP address information."""
    address: str
    version: int
    is_private: bool
    is_loopback: bool
    is_link_local: bool
    is_multicast: bool
    is_unspecified: bool
    is_reserved: bool
    is_global: bool
    network: Optional[str] = None
    broadcast: Optional[str] = None
    netmask: Optional[str] = None
    prefixlen: Optional[int] = None
    hosts: Optional[int] = None
    compressed: Optional[str] = None
    exploded: Optional[str] = None


class IPAddress(ABC):
    """Abstract base class for IP addresses."""
    
    def __init__(self, address: str):
        """
        Initialize with an IP address string.
        
        Args:
            address: String representation of IP address
            
        Raises:
            ValueError: If the address is not a valid IP address
        """
        self._original_address = address
        self._address_obj = None
        self._parse_address(address)
    
    @abstractmethod
    def _parse_address(self, address: str) -> None:
        """Parse and validate the IP address."""
        pass
    
    @property
    def address(self) -> str:
        """Return the original address string."""
        return self._original_address
    
    @property
    def version(self) -> int:
        """Return the IP version (4 or 6)."""
        return self._address_obj.version
    
    @property
    def is_private(self) -> bool:
        """Check if the address is private."""
        return self._address_obj.is_private
    
    @property
    def is_loopback(self) -> bool:
        """Check if the address is a loopback address."""
        return self._address_obj.is_loopback
    
    @property
    def is_link_local(self) -> bool:
        """Check if the address is link-local."""
        return self._address_obj.is_link_local
    
    @property
    def is_multicast(self) -> bool:
        """Check if the address is multicast."""
        return self._address_obj.is_multicast
    
    @property
    def is_unspecified(self) -> bool:
        """Check if the address is unspecified."""
        return self._address_obj.is_unspecified
    
    @property
    def is_reserved(self) -> bool:
        """Check if the address is reserved."""
        return self._address_obj.is_reserved
    
    @property
    def is_global(self) -> bool:
        """Check if the address is globally reachable."""
        return self._address_obj.is_global
    
    @property
    def compressed(self) -> str:
        """Return the compressed representation."""
        return str(self._address_obj)
    
    @property
    def exploded(self) -> str:
        """Return the exploded (full) representation for IPv6."""
        return self._address_obj.exploded
    
    def __str__(self) -> str:
        """Return string representation."""
        return str(self._address_obj)
    
    def __repr__(self) -> str:
        """Return formal string representation."""
        return f"{self.__class__.__name__}('{self._original_address}')"
    
    def __eq__(self, other) -> bool:
        """Check equality with another IP address."""
        if isinstance(other, IPAddress):
            return str(self._address_obj) == str(other._address_obj)
        return NotImplemented
    
    def __lt__(self, other) -> bool:
        """Compare if this address is less than another."""
        if isinstance(other, IPAddress):
            return int(self._address_obj) < int(other._address_obj)
        return NotImplemented
    
    def __hash__(self) -> int:
        """Return hash of the IP address."""
        return hash(str(self._address_obj))
    
    def to_info(self) -> IPInfo:
        """Return IPInfo dataclass with all address information."""
        return IPInfo(
            address=self._original_address,
            version=self.version,
            is_private=self.is_private,
            is_loopback=self.is_loopback,
            is_link_local=self.is_link_local,
            is_multicast=self.is_multicast,
            is_unspecified=self.is_unspecified,
            is_reserved=self.is_reserved,
            is_global=self.is_global,
            compressed=self.compressed,
            exploded=self.exploded,
        )


class IPv4Address(IPAddress):
    """IPv4 address representation."""
    
    def __init__(self, address: str):
        """
        Initialize IPv4 address.
        
        Args:
            address: IPv4 address string (e.g., '192.168.1.1')
            
        Raises:
            ValueError: If the address is not a valid IPv4 address
        """
        super().__init__(address)
    
    def _parse_address(self, address: str) -> None:
        """Parse and validate the IPv4 address."""
        try:
            self._address_obj = ipaddress.IPv4Address(address)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IPv4 address: {address}") from e
    
    def in_network(self, network: str) -> bool:
        """
        Check if this address is in the given network.
        
        Args:
            network: Network string in CIDR notation (e.g., '192.168.1.0/24')
            
        Returns:
            True if address is in the network, False otherwise
        """
        try:
            net = ipaddress.IPv4Network(network, strict=False)
            return self._address_obj in net
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError) as e:
            raise ValueError(f"Invalid network: {network}") from e


class IPv6Address(IPAddress):
    """IPv6 address representation."""
    
    def __init__(self, address: str):
        """
        Initialize IPv6 address.
        
        Args:
            address: IPv6 address string (e.g., '2001:db8::1')
            
        Raises:
            ValueError: If the address is not a valid IPv6 address
        """
        super().__init__(address)
    
    def _parse_address(self, address: str) -> None:
        """Parse and validate the IPv6 address."""
        try:
            self._address_obj = ipaddress.IPv6Address(address)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid IPv6 address: {address}") from e
    
    def scope(self) -> Optional[str]:
        """
        Get the scope of the IPv6 address.
        
        Returns:
            Scope string or None if not applicable
        """
        # Check for link-local addresses
        if self.is_link_local:
            return "link-local"
        # Check for unique local addresses (ULA)
        if self._address_obj.is_private:
            return "unique-local"
        # Check for global addresses
        if self.is_global:
            return "global"
        return None


class IPFactory:
    """Factory class for creating IP address objects."""
    
    @staticmethod
    def create(address: str) -> IPAddress:
        """
        Create an IP address object based on the address version.
        
        Args:
            address: IP address string
            
        Returns:
            IPv4Address or IPv6Address instance
            
        Raises:
            ValueError: If the address is not valid
        """
        if not address or not isinstance(address, str):
            raise ValueError("Address must be a non-empty string")
        
        # Use ipaddress module to determine version first
        import ipaddress
        try:
            # Check if it's valid IP first
            temp_addr = ipaddress.ip_address(address)
            if temp_addr.version == 4:
                return IPv4Address(address)
            else:
                return IPv6Address(address)
        except ValueError:
            pass
        
        raise ValueError(f"Invalid IP address: {address}")
    
    @staticmethod
    def create_from_int(value: int, version: int = 4) -> IPAddress:
        """
        Create an IP address from an integer.
        
        Args:
            value: Integer representation of the IP address
            version: IP version (4 or 6)
            
        Returns:
            IPv4Address or IPv6Address instance
            
        Raises:
            ValueError: If the value is not valid for the given version
        """
        if version == 4:
            return IPv4Address(str(ipaddress.IPv4Address(value)))
        elif version == 6:
            return IPv6Address(str(ipaddress.IPv6Address(value)))
        else:
            raise ValueError(f"Invalid IP version: {version}")

"""
IP address validation functions.

This module provides validation functions for IP addresses,
network specifications, and related operations.
"""

import re
import ipaddress
from typing import Optional, Tuple, List


class IPValidator:
    """Class containing IP validation functions."""
    
    # Regular expressions for various IP formats
    IPv4_PATTERN = r"""
        ^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}
        (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
    """
    
    IPv6_PATTERN = r"""
        ^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$        # Standard IPv6
        |^(?:[0-9a-fA-F]{1,4}:){1,7}:$                    # With trailing colon
        |^(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}$    # With :: at end
        |^(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}$
        |^(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}$
        |^(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}$
        |^(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}$
        |^[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})$
        |^:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)$
        |^fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-fA-F]{1,4}$
        |^::(?:ffff(?::0{1,4}){0,1}:){0,1}[0-9a-fA-F]{1,4}:(?:(?:25[0-5]|
          2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|
          [01]?[0-9][0-9]?)$
        |^(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|2[0-4][0-9]|
          [01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
    """
    
    @staticmethod
    def is_valid_ipv4(address: str) -> bool:
        """
        Check if the address is a valid IPv4 address.
        
        Args:
            address: String to validate
            
        Returns:
            True if valid IPv4 address, False otherwise
        """
        try:
            ipaddress.IPv4Address(address)
            return True
        except ipaddress.AddressValueError:
            return False
    
    @staticmethod
    def is_valid_ipv6(address: str) -> bool:
        """
        Check if the address is a valid IPv6 address.
        
        Args:
            address: String to validate
            
        Returns:
            True if valid IPv6 address, False otherwise
        """
        try:
            ipaddress.IPv6Address(address)
            return True
        except ipaddress.AddressValueError:
            return False
    
    @staticmethod
    def is_valid_ip(address: str) -> bool:
        """
        Check if the address is a valid IP address (IPv4 or IPv6).
        
        Args:
            address: String to validate
            
        Returns:
            True if valid IP address, False otherwise
        """
        return IPValidator.is_valid_ipv4(address) or IPValidator.is_valid_ipv6(address)
    
    @staticmethod
    def is_valid_network(network: str, strict: bool = False) -> bool:
        """
        Check if the string is a valid network specification.
        
        Args:
            network: String to validate (e.g., '192.168.1.0/24')
            strict: If True, raise exception for network addresses with host bits set
            
        Returns:
            True if valid network, False otherwise
        """
        try:
            ipaddress.ip_network(network, strict=strict)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_ip_version(address: str) -> Optional[int]:
        """
        Determine the IP version of an address.
        
        Args:
            address: IP address string
            
        Returns:
            IP version (4 or 6) or None if invalid
        """
        if IPValidator.is_valid_ipv4(address):
            return 4
        if IPValidator.is_valid_ipv6(address):
            return 6
        return None
    
    @staticmethod
    def is_private_ip(address: str) -> bool:
        """
        Check if an address is a private IP address.
        
        Args:
            address: IP address string
            
        Returns:
            True if private IP address, False otherwise
        """
        try:
            ip_obj = ipaddress.ip_address(address)
            return ip_obj.is_private
        except ValueError:
            return False
    
    @staticmethod
    def is_loopback(address: str) -> bool:
        """
        Check if an address is a loopback address.
        
        Args:
            address: IP address string
            
        Returns:
            True if loopback address, False otherwise
        """
        try:
            ip_obj = ipaddress.ip_address(address)
            return ip_obj.is_loopback
        except ValueError:
            return False
    
    @staticmethod
    def is_multicast(address: str) -> bool:
        """
        Check if an address is a multicast address.
        
        Args:
            address: IP address string
            
        Returns:
            True if multicast address, False otherwise
        """
        try:
            ip_obj = ipaddress.ip_address(address)
            return ip_obj.is_multicast
        except ValueError:
            return False
    
    @staticmethod
    def is_link_local(address: str) -> bool:
        """
        Check if an address is a link-local address.
        
        Args:
            address: IP address string
            
        Returns:
            True if link-local address, False otherwise
        """
        try:
            ip_obj = ipaddress.ip_address(address)
            return ip_obj.is_link_local
        except ValueError:
            return False
    
    @staticmethod
    def is_global(address: str) -> bool:
        """
        Check if an address is globally reachable.
        
        Args:
            address: IP address string
            
        Returns:
            True if globally reachable, False otherwise
        """
        try:
            ip_obj = ipaddress.ip_address(address)
            return ip_obj.is_global
        except ValueError:
            return False
    
    @staticmethod
    def get_network_range(network: str) -> Tuple[str, str]:
        """
        Get the network and broadcast addresses for a given network.
        
        Args:
            network: Network specification (e.g., '192.168.1.0/24')
            
        Returns:
            Tuple of (network_address, broadcast_address)
            
        Raises:
            ValueError: If the network specification is invalid
        """
        try:
            net = ipaddress.ip_network(network, strict=False)
            return str(net.network_address), str(net.broadcast_address)
        except ValueError as e:
            raise ValueError(f"Invalid network specification: {e}") from e
    
    @staticmethod
    def is_overlap(network1: str, network2: str) -> bool:
        """
        Check if two networks overlap.
        
        Args:
            network1: First network specification
            network2: Second network specification
            
        Returns:
            True if networks overlap, False otherwise
        """
        try:
            net1 = ipaddress.ip_network(network1, strict=False)
            net2 = ipaddress.ip_network(network2, strict=False)
            return net1.overlaps(net2)
        except ValueError as e:
            raise ValueError(f"Invalid network specification: {e}") from e
    
    @staticmethod
    def parse_cidr(cidr: str) -> Tuple[str, int]:
        """Parse CIDR notation.
        
        Args:
            cidr: CIDR notation string (e.g., '192.168.1.0/24')
            
        Returns:
            Tuple of (base_address, prefix_length)
            
        Raises:
            ValueError: If the CIDR notation is invalid
        """
        try:
            net = ipaddress.ip_network(cidr, strict=False)
            return str(net.network_address), net.prefixlen
        except ValueError as e:
            raise ValueError(f"Invalid CIDR notation: {e}") from e
    
    @staticmethod
    def is_valid_port(port: int) -> bool:
        """
        Check if a port number is valid.
        
        Args:
            port: Port number to validate
            
        Returns:
            True if valid port (1-65535), False otherwise
        """
        return 1 <= port <= 65535
    
    @staticmethod
    def is_valid_port_range(port_range: str) -> bool:
        """
        Check if a port range is valid.
        
        Args:
            port_range: Port range string (e.g., '80-443' or '80')
            
        Returns:
            True if valid port range, False otherwise
        """
        try:
            if '-' in port_range:
                parts = port_range.split('-')
                if len(parts) != 2:
                    return False
                start = int(parts[0])
                end = int(parts[1])
                return IPValidator.is_valid_port(start) and IPValidator.is_valid_port(end) and start <= end
            else:
                return IPValidator.is_valid_port(int(port_range))
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def normalize_ipv6(address: str) -> str:
        """
        Normalize an IPv6 address to compressed form.
        
        Args:
            address: IPv6 address to normalize
            
        Returns:
            Compressed IPv6 address string
            
        Raises:
            ValueError: If the address is not valid
        """
        try:
            ip_obj = ipaddress.IPv6Address(address)
            return str(ip_obj)
        except ValueError as e:
            raise ValueError(f"Invalid IPv6 address: {e}") from e
    
    @staticmethod
    def expand_ipv6(address: str) -> str:
        """
        Expand an IPv6 address to full form.
        
        Args:
            address: IPv6 address to expand
            
        Returns:
            Expanded IPv6 address string
            
        Raises:
            ValueError: If the address is not valid
        """
        try:
            ip_obj = ipaddress.IPv6Address(address)
            return ip_obj.exploded
        except ValueError as e:
            raise ValueError(f"Invalid IPv6 address: {e}") from e

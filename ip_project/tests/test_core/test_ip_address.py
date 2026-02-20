"""
Unit tests for core IP address functionality.
"""

import unittest
from ip_project.core.ip_address import IPFactory, IPv4Address, IPv6Address
from ip_project.core.validators import IPValidator


class TestIPFactory(unittest.TestCase):
    """Tests for IPFactory class."""
    
    def test_create_ipv4(self):
        """Test creating IPv4 address."""
        ip = IPFactory.create("192.168.1.1")
        self.assertIsInstance(ip, IPv4Address)
        self.assertEqual(str(ip), "192.168.1.1")
    
    def test_create_ipv6(self):
        """Test creating IPv6 address."""
        ip = IPFactory.create("2001:db8::1")
        self.assertIsInstance(ip, IPv6Address)
    
    def test_create_invalid(self):
        """Test creating invalid IP."""
        with self.assertRaises(ValueError):
            IPFactory.create("invalid")
    
    def test_create_from_int(self):
        """Test creating IP from integer."""
        ip = IPFactory.create_from_int(3232235777, 4)
        self.assertEqual(str(ip), "192.168.1.1")


class TestIPv4Address(unittest.TestCase):
    """Tests for IPv4Address class."""
    
    def test_valid_addresses(self):
        """Test valid IPv4 addresses."""
        valid = [
            "192.168.1.1",
            "10.0.0.1",
            "127.0.0.1",
            "8.8.8.8",
        ]
        for addr in valid:
            ip = IPv4Address(addr)
            self.assertEqual(str(ip), addr)
    
    def test_private_ip(self):
        """Test private IP detection."""
        ip = IPv4Address("192.168.1.1")
        self.assertTrue(ip.is_private)
    
    def test_loopback(self):
        """Test loopback detection."""
        ip = IPv4Address("127.0.0.1")
        self.assertTrue(ip.is_loopback)


class TestIPv6Address(unittest.TestCase):
    """Tests for IPv6Address class."""
    
    def test_compressed_form(self):
        """Test IPv6 compressed form."""
        ip = IPv6Address("2001:0db8:0000:0000:0000:0000:0000:0001")
        self.assertEqual(str(ip), "2001:db8::1")
    
    def test_expanded_form(self):
        """Test IPv6 expanded form."""
        ip = IPv6Address("2001:db8::1")
        self.assertEqual(ip.exploded, "2001:0db8:0000:0000:0000:0000:0000:0001")


class TestIPValidator(unittest.TestCase):
    """Tests for IPValidator class."""
    
    def test_valid_ipv4(self):
        """Test IPv4 validation."""
        self.assertTrue(IPValidator.is_valid_ipv4("192.168.1.1"))
        self.assertFalse(IPValidator.is_valid_ipv4("invalid"))
    
    def test_valid_ipv6(self):
        """Test IPv6 validation."""
        self.assertTrue(IPValidator.is_valid_ipv6("2001:db8::1"))
        self.assertFalse(IPValidator.is_valid_ipv6("invalid"))
    
    def test_get_version(self):
        """Test IP version detection."""
        self.assertEqual(IPValidator.get_ip_version("192.168.1.1"), 4)
        self.assertEqual(IPValidator.get_ip_version("2001:db8::1"), 6)


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for public IP detection service.
"""

import unittest
from ip_project.services.public_ip import PublicIPDetector, IPService


class TestPublicIPDetector(unittest.TestCase):
    """Tests for PublicIPDetector class."""
    
    def test_default_services(self):
        """Test default services configuration."""
        detector = PublicIPDetector()
        services = detector.get_available_services()
        self.assertGreater(len(services), 0)
    
    def test_add_service(self):
        """Test adding a new service."""
        detector = PublicIPDetector()
        detector.add_service("test", "https://example.com/ip", 5)
        services = detector.get_available_services()
        service_names = [s.name for s in services]
        self.assertIn("test", service_names)
    
    def test_remove_service(self):
        """Test removing a service."""
        detector = PublicIPDetector()
        result = detector.remove_service("ipify")
        self.assertTrue(result)


class TestIPService(unittest.TestCase):
    """Tests for IPService dataclass."""
    
    def test_service_creation(self):
        """Test creating an IPService."""
        service = IPService("test", "https://example.com", 10, True)
        self.assertEqual(service.name, "test")
        self.assertEqual(service.url, "https://example.com")
        self.assertEqual(service.timeout, 10)
        self.assertTrue(service.enabled)


if __name__ == "__main__":
    unittest.main()

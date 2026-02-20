"""
Unit tests for DNS resolver service.
"""

import unittest
from ip_project.services.resolution import DNSResolver


class TestDNSResolver(unittest.TestCase):
    """Tests for DNSResolver class."""
    
    def test_resolve_localhost(self):
        """Test resolving localhost."""
        resolver = DNSResolver(enable_cache=False)
        result = resolver.resolve("localhost")
        self.assertIsNotNone(result)
    
    def test_cache(self):
        """Test DNS caching."""
        resolver = DNSResolver(enable_cache=True)
        result1 = resolver.resolve("localhost")
        result2 = resolver.resolve("localhost")
        self.assertEqual(result1, result2)


if __name__ == "__main__":
    unittest.main()

"""
Services module for external IP-related services.

This module provides integrations with external services for
public IP detection, DNS resolution, and other network services.
"""

from ip_project.services.public_ip import PublicIPDetector
from ip_project.services.resolution import DNSResolver

__all__ = [
    "PublicIPDetector",
    "DNSResolver",
]

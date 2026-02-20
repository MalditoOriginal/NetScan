"""
Main controller for IP Definition GUI.

This module provides the main controller that orchestrates the GUI
and connects views with the core functionality.
"""

from typing import Any
import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style

from ip_project.core import IPFactory, IPValidator
from ip_project.services import PublicIPDetector, DNSResolver
from ip_project.utils import get_logger


class MainController:
    """
    Main controller for the IP Definition GUI.
    
    Handles all business logic and coordinates between views and models.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main controller.
        
        Args:
            root: Root window
        """
        self._logger = get_logger(self.__class__.__name__)
        self._root = root
        self._public_ip_detector = PublicIPDetector()
        self._dns_resolver = DNSResolver()
        
        # Initialize view references
        self._ip_input_view = None
        self._results_view = None
        self._examples_view = None
        
        self._logger.info("MainController initialized")
    
    def attach_view(self, view: Any) -> None:
        """Attach a view to the controller."""
        view_class = view.__class__.__name__
        if "IPInputView" == view_class:
            self._ip_input_view = view
        elif "ResultsView" == view_class:
            self._results_view = view
        elif "ExamplesView" == view_class:
            self._examples_view = view
        self._logger.debug(f"Attached view: {view_class}")
    
    def analyze_ip(self, ip_address: str) -> None:
        """Analyze an IP address and display results."""
        self._logger.info(f"Analyzing IP: {ip_address}")
        
        # Validate IP
        if not IPValidator.is_valid_ip(ip_address):
            self._show_result(f"Error: Invalid IP address: {ip_address}", "error")
            return
        
        try:
            ip_obj = IPFactory.create(ip_address)
            info = ip_obj.to_info()
            
            self._show_result(f"\n{'=' * 50}\n", "header")
            self._show_result(f"IP Address: {info.address}\n", "default")
            self._show_result(f"{'=' * 50}\n", "header")
            
            # Basic info
            self._show_result("\n--- Basic Information ---\n", "info")
            self._show_result(f"  Version: IPv{info.version}\n", "success")
            self._show_result(f"  Compressed: {info.compressed}\n", "default")
            self._show_result(f"  Expanded: {info.exploded}\n", "default")
            self._show_result(f"  Is Private: {'Yes' if info.is_private else 'No'}\n", "success")
            self._show_result(f"  Is Loopback: {'Yes' if info.is_loopback else 'No'}\n", "success")
            self._show_result(f"  Is Global: {'Yes' if info.is_global else 'No'}\n", "success")
            
            # Network info
            if info.network:
                self._show_result("\n--- Network Information ---\n", "info")
                self._show_result(f"  Network: {info.network}\n", "default")
                self._show_result(f"  Netmask: {info.netmask}\n", "default")
            
            # DNS resolution
            hostname = self._dns_resolver.reverse_resolve(ip_address)
            if hostname:
                self._show_result("\n--- Hostname ---\n", "info")
                self._show_result(f"  Hostname: {hostname}\n", "default")
            
            self._logger.info(f"Analysis complete for {ip_address}")
            
        except Exception as e:
            self._show_result(f"Error analyzing IP: {e}", "error")
            self._logger.error(f"Analysis failed for {ip_address}: {e}")
    
    def get_public_ip(self) -> None:
        """Get and display the public IP address."""
        self._logger.info("Fetching public IP")
        ip = self._public_ip_detector.detect_public_ip()
        
        if ip:
            self._show_result(f"\n{'=' * 50}\n", "header")
            self._show_result(f"Public IP: {ip}\n", "success")
            self._show_result(f"{'=' * 50}\n", "header")
            
            # Analyze the public IP
            self.analyze_ip(ip)
        else:
            self._show_result("Failed to detect public IP. Check your internet connection.", "error")
            self._logger.error("Public IP detection failed")
    
    def resolve_hostname(self, hostname: str) -> None:
        """Resolve a hostname to an IP address."""
        self._logger.info(f"Resolving hostname: {hostname}")
        ip = self._dns_resolver.resolve(hostname)
        
        if ip:
            self._show_result(f"\n{'=' * 50}\n", "header")
            self._show_result(f"Hostname: {hostname}\n", "default")
            self._show_result(f"IP: {ip}\n", "success")
            self._show_result(f"{'=' * 50}\n", "header")
            
            # Analyze the resolved IP
            self.analyze_ip(ip)
        else:
            self._show_result(f"Failed to resolve hostname: {hostname}", "error")
            self._logger.error(f"DNS resolution failed for {hostname}")
    
    def _show_result(self, text: str, tag: str = "default") -> None:
        """Show a result in the results view."""
        if self._results_view:
            self._results_view.append_result(text, tag)
    
    def clear_results(self) -> None:
        """Clear all results from the display."""
        if self._results_view:
            self._results_view.clear_results()

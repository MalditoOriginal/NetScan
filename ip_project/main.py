#!/usr/bin/env python3
"""
IP Definition Application - Main Entry Point

This module provides the main application entry point for the IP Definition
project with support for multiple interfaces (CLI, GUI, API).

Usage:
    python -m ip_project.main          # Run GUI application
    python -m ip_project.main cli      # Run CLI application
    python -m ip_project.main api      # Start API server
"""

import sys
import argparse


# Import ttkbootstrap at module level
import ttkbootstrap
from ttkbootstrap.constants import *

import tkinter as tk


def run_gui():
    """Run the modern GUI application with ttkbootstrap theming."""
    try:
        pass  # Already imported
    except ImportError as e:
        print(f"Error: GUI requires ttkbootstrap - pip install ttkbootstrap")
        return 1
    
    from ip_project.gui.base import ModernGUI
    from ip_project.core import IPFactory, IPValidator
    from ip_project.services import PublicIPDetector, DNSResolver
    
    class AppController:
        """Controller for the modern GUI."""
        
        def __init__(self, app):
            self.app = app
            self.public_detector = PublicIPDetector()
            self.dns_resolver = DNSResolver()
            
            # Register observers
            self.app.add_observer(self)
        
        def update(self, data):
            """Handle observer updates."""
            if data["type"] == "analyze":
                self._analyze_ip(data["ip"])
            elif data["type"] == "public_ip":
                self._get_public_ip()
            elif data["type"] == "local_ip":
                self._get_local_ip()
            elif data["type"] == "ipv4_examples":
                self._show_ipv4_examples()
            elif data["type"] == "ipv6_examples":
                self._show_ipv6_examples()
        
        def _analyze_ip(self, ip_address):
            """Analyze and display IP address."""
            self.app.status_var.set(f"Analyzing: {ip_address}")
            
            if not IPValidator.is_valid_ip(ip_address):
                self.app.append_result(f"Error: Invalid IP address: {ip_address}\n", "error")
                return
            
            try:
                ip_obj = IPFactory.create(ip_address)
                info = ip_obj.to_info()
                
                self.app.append_result(f"\n{'=' * 50}\n", "header")
                self.app.append_result(f"IP Address: {info.address}\n", "default")
                self.app.append_result(f"{'=' * 50}\n", "header")
                
                self.app.append_result("\n--- Basic Information ---\n", "info")
                self.app.append_result(f"  Version: IPv{info.version}\n", "success")
                self.app.append_result(f"  Compressed: {info.compressed}\n", "default")
                self.app.append_result(f"  Is Private: {'Yes' if info.is_private else 'No'}\n", "success")
                self.app.append_result(f"  Is Loopback: {'Yes' if info.is_loopback else 'No'}\n", "success")
                self.app.append_result(f"  Is Global: {'Yes' if info.is_global else 'No'}\n", "success")
                
                if info.is_global:
                    self.app.append_result("  Status: ✓ Public IP (globally reachable)\n", "success")
                else:
                    self.app.append_result("  Status: ✓ Private IP (internal network)\n", "info")
                    
            except Exception as e:
                self.app.append_result(f"Error: {e}\n", "error")
        
        def _get_public_ip(self):
            """Get and display public IP."""
            self.app.append_result(f"\n{'=' * 50}\n", "header")
            self.app.append_result("--- Public IP Detection ---\n", "info")
            self.app.append_result(f"{'=' * 50}\n", "header")
            
            ip = self.public_detector.detect_public_ip()
            if ip:
                self.app.append_result(f"Public IP: {ip}\n", "success")
                self.app.append_result(f"Service used: {self.public_detector.get_last_used_service()}\n", "info")
                self._analyze_ip(ip)
            else:
                self.app.append_result("Failed to detect public IP. Check connection.\n", "error")
        
        def _get_local_ip(self):
            """Get and display local IP."""
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                self.app.append_result(f"\n{'=' * 50}\n", "header")
                self.app.append_result(f"Local IP Address: {local_ip}\n", "info")
                self.app.append_result(f"{'=' * 50}\n", "header")
                self._analyze_ip(local_ip)
            except Exception as e:
                self.app.append_result(f"Error getting local IP: {e}\n", "error")
        
        def _show_ipv4_examples(self):
            """Show IPv4 examples."""
            examples = [
                ("192.168.1.1", "Router/Gateway - Private"),
                ("10.0.0.1", "Private Network"),
                ("127.0.0.1", "Loopback"),
                ("8.8.8.8", "Google DNS - Global"),
                ("172.16.0.1", "Private Network"),
            ]
            
            self.app.append_result(f"\n{'=' * 50}\n", "header")
            self.app.append_result("--- IPv4 Examples ---\n", "info")
            self.app.append_result(f"{'=' * 50}\n", "header")
            
            for addr, desc in examples:
                self.app.append_result(f"\n{addr} - {desc}\n", "default")
                try:
                    ip = IPFactory.create(addr)
                    self.app.append_result(f"  Version: IPv{ip.version}\n", "success")
                    self.app.append_result(f"  Status: {'Global' if ip.is_global else 'Private'}\n", "info")
                except Exception as e:
                    self.app.append_result(f"  Error: {e}\n", "error")
        
        def _show_ipv6_examples(self):
            """Show IPv6 examples."""
            examples = [
                ("2001:4860:4860::8888", "Google DNS"),
                ("::1", "Loopback"),
                ("fe80::1", "Link-local"),
            ]
            
            self.app.append_result(f"\n{'=' * 50}\n", "header")
            self.app.append_result("--- IPv6 Examples ---\n", "info")
            self.app.append_result(f"{'=' * 50}\n", "header")
            
            for addr, desc in examples:
                self.app.append_result(f"\n{addr} - {desc}\n", "default")
                try:
                    ip = IPFactory.create(addr)
                    self.app.append_result(f"  Version: IPv{ip.version}\n", "success")
                    self.app.append_result(f"  Compressed: {ip.compressed}\n", "default")
                except Exception as e:
                    self.app.append_result(f"  Error: {e}\n", "error")
    
    # Create and run the app
    app = ModernGUI(title="IP Definition Program - Modern")
    controller = AppController(app)
    app.mainloop()
    return 0


def run_cli():
    """Run the CLI application."""
    parser = argparse.ArgumentParser(
        description="IP Definition Tool - Analyze IP addresses from command line"
    )
    parser.add_argument("ip", nargs="?", help="IP address to analyze")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-p", "--public", action="store_true", help="Show public IP address"
    )
    parser.add_argument(
        "-l", "--local", action="store_true", help="Show local IP address"
    )
    
    args = parser.parse_args()
    
    if args.public:
        from ip_project.services import PublicIPDetector
        detector = PublicIPDetector()
        ip = detector.detect_public_ip()
        print(f"Public IP: {ip}" if ip else "Failed to detect public IP")
        return 0
    
    if args.local:
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            print(f"Local IP: {s.getsockname()[0]}")
            s.close()
        except Exception as e:
            print(f"Error getting local IP: {e}")
            return 1
        return 0
    
    if args.ip:
        from ip_project.core import IPFactory, IPValidator
        from ip_project.services import DNSResolver
        
        # Validate IP
        if not IPValidator.is_valid_ip(args.ip):
            print(f"Error: Invalid IP address: {args.ip}")
            return 1
        
        # Create IP object
        try:
            ip_obj = IPFactory.create(args.ip)
            info = ip_obj.to_info()
            
            print(f"\n=== IP Address Analysis ===\n")
            print(f"Address: {info.address}")
            print(f"Version: IPv{info.version}")
            print(f"Compressed: {info.compressed}")
            print(f"Is Private: {info.is_private}")
            print(f"Is Loopback: {info.is_loopback}")
            print(f"Is Global: {info.is_global}")
            
            if args.verbose:
                print(f"Is Link Local: {info.is_link_local}")
                print(f"Is Multicast: {info.is_multicast}")
                print(f"Is Unspecified: {info.is_unspecified}")
                print(f"Is Reserved: {info.is_reserved}")
                
                # Try DNS resolution
                resolver = DNSResolver()
                hostname = resolver.reverse_resolve(args.ip)
                if hostname:
                    print(f"Hostname: {hostname}")
        except Exception as e:
            print(f"Error analyzing IP: {e}")
            return 1
    else:
        parser.print_help()
    
    return 0


def run_api():
    """Run the API server."""
    try:
        from flask import Flask, jsonify
    except ImportError:
        print("Error: API requires Flask: pip install flask")
        return 1
    
    app = Flask(__name__)
    
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy"})
    
    @app.route("/api/analyze/<ip_address>", methods=["GET"])
    def analyze_ip(ip_address):
        from ip_project.core import IPFactory, IPValidator
        
        if not IPValidator.is_valid_ip(ip_address):
            return jsonify({"error": f"Invalid IP: {ip_address}"}), 400
        
        try:
            ip_obj = IPFactory.create(ip_address)
            info = ip_obj.to_info()
            return jsonify({
                "address": info.address,
                "version": info.version,
                "compressed": info.compressed,
                "is_private": info.is_private,
                "is_loopback": info.is_loopback,
                "is_global": info.is_global,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/public-ip", methods=["GET"])
    def public_ip():
        from ip_project.services import PublicIPDetector
        detector = PublicIPDetector()
        ip = detector.detect_public_ip()
        if ip:
            return jsonify({"ip": ip})
        return jsonify({"error": "Failed to detect public IP"}), 500
    
    print("Starting API server on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="IP Definition Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ip_project.main           # Run GUI
  python -m ip_project.main cli       # Run CLI
  python -m ip_project.main cli 8.8.8.8  # Analyze IP via CLI
  python -m ip_project.main api       # Start API server
        """
    )
    parser.add_argument(
        "mode", nargs="?", default="gui",
        choices=["gui", "cli", "api"],
        help="Application mode (default: gui)"
    )
    parser.add_argument(
        "args", nargs=argparse.REMAINDER,
        help="Mode-specific arguments"
    )
    
    args = parser.parse_args()
    
    # Rebuild sys.argv for sub-modes
    if args.args:
        sys.argv = [sys.argv[0]] + args.args
    
    if args.mode == "gui":
        return run_gui()
    elif args.mode == "cli":
        return run_cli()
    elif args.mode == "api":
        return run_api()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

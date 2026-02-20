#!/usr/bin/env python3
"""
IP Network Analysis Tool

A comprehensive tool for IP address analysis, network calculations,
public IP detection, and DNS resolution with modern GUI interface.

Usage:
    python main.py          # Run GUI application
    python main.py cli      # Run CLI application
    python main.py api      # Start API server

Features:
    - IPv4/IPv6 address analysis
    - Network calculations and subnetting
    - Public IP detection from multiple services
    - DNS resolution with caching
    - Modern ttkbootstrap GUI
"""

import sys


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print(__doc__)
        return 0
    
    from ip_project.main import run_cli, run_gui, run_api
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="ip-analyzer",
        description="IP Network Analysis Tool - Comprehensive IP analysis utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ip-analyzer           # Run GUI application
  ip-analyzer cli       # Run CLI mode
  ip-analyzer cli 8.8.8.8  # Analyze IP via CLI
  ip-analyzer api       # Start API server on port 5000
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
        print(__doc__)
        return 1


if __name__ == "__main__":
    sys.exit(main())

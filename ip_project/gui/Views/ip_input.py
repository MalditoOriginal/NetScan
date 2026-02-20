"""
IP Input view component for the IP Definition GUI.

This module provides the user interface for IP address input
and related actions.
"""

from typing import Any
import tkinter as tk
from tkinter import ttk


class IPInputView(ttk.Frame):
    """
    View for IP address input and selection.
    
    Provides input fields for IP addresses, hostname resolution,
    and public IP detection with history tracking.
    """
    
    def __init__(self, parent: tk.Widget, controller: Any = None):
        """
        Initialize the IP input view.
        
        Args:
            parent: Parent widget
            controller: Controller instance
        """
        super().__init__(parent)
        self._controller = controller
        self._history: list = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the IP input UI."""
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # IP Input section
        input_frame = ttk.LabelFrame(main_frame, text="IP Address Input")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Address entry
        ttk.Label(input_frame, text="IP Address:").pack(anchor=tk.W, padx=5, pady=5)
        self._addr_var = tk.StringVar()
        self._addr_entry = ttk.Entry(input_frame, textvariable=self._addr_var)
        self._addr_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        self._addr_entry.bind('<Return>', lambda e: self._on_analyze())
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, padx=5)
        
        ttk.Button(
            button_frame,
            text="Analyze",
            command=self._on_analyze
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Get Public IP",
            command=self._on_get_public_ip
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="Resolve Hostname",
            command=self._on_resolve_hostname
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Hostname input (hidden by default)
        self._hostname_frame = ttk.Frame(input_frame)
        self._hostname_var = tk.StringVar()
        ttk.Label(self._hostname_frame, text="Hostname:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(self._hostname_frame, textvariable=self._hostname_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(self._hostname_frame, text="Resolve",
                  command=self._on_resolve_hostname).pack(side=tk.LEFT, padx=(5, 0))
        
        # History section
        history_frame = ttk.LabelFrame(main_frame, text="History")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # History listbox
        list_frame = ttk.Frame(history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self._history_list = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            height=5
        )
        scrollbar.config(command=self._history_list.yview)
        
        self._history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Clear history button
        ttk.Button(
            history_frame,
            text="Clear History",
            command=self._on_clear_history
        ).pack(pady=5)
    
    def _on_analyze(self) -> None:
        """Handle analyze button click."""
        address = self._addr_var.get().strip()
        if address and self._controller:
            self._controller.analyze_ip(address)
    
    def _on_get_public_ip(self) -> None:
        """Handle get public IP button click."""
        if self._controller:
            self._controller.get_public_ip()
    
    def _on_resolve_hostname(self) -> None:
        """Handle resolve hostname button click."""
        hostname = self._hostname_var.get().strip()
        if hostname and self._controller:
            self._controller.resolve_hostname(hostname)
    
    def _on_clear_history(self) -> None:
        """Handle clear history button click."""
        self._history.clear()
        self._history_list.delete(0, tk.END)
    
    def update_view(self, data: Any) -> None:
        """Update the view with new data."""
        if data and data.get("type") == "history":
            self._history = data.get("history", [])
            self._history_list.delete(0, tk.END)
            for item in self._history:
                self._history_list.insert(tk.END, item)
    
    def add_to_history(self, item: str) -> None:
        """Add an item to history."""
        if item not in self._history:
            self._history.insert(0, item)
            if len(self._history) > 10:
                self._history.pop()
            self._history_list.insert(0, item)

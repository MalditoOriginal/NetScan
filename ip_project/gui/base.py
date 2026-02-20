"""
Modern GUI module with ttkbootstrap theming.

This module provides base classes with ttkbootstrap for modern
button styles, sidebar, and modern widget styling.
"""

from abc import ABC, abstractmethod
from typing import List, Callable, Any, Optional
import tkinter as tk
from tkinter import ttk, scrolledtext
import ttkbootstrap as tb
from ttkbootstrap.constants import *


class GUIObserver(ABC):
    """Abstract base class for GUI observers."""
    
    @abstractmethod
    def update(self, data: Any) -> None:
        """Update the observer with new data."""
        pass


class GUIObservable:
    """Base class for observable objects in the GUI."""
    
    def __init__(self):
        self._observers: List[GUIObserver] = []
    
    def add_observer(self, observer: GUIObserver) -> None:
        """Add an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: GUIObserver) -> None:
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, data: Any = None) -> None:
        """Notify all observers with new data."""
        for observer in self._observers:
            observer.update(data)


class ModernGUI(tb.Tk):
    """Modern GUI application with ttkbootstrap theming."""
    
    def __init__(self, title: str = "IP Definition Program", theme: str = "darkly"):
        """
        Initialize the modern GUI.
        
        Args:
            title: Window title
            theme: ttkbootstrap theme name
        """
        # Initialize ttkbootstrap Tk with style
        tb.Tk.__init__(self)
        self.style = tb.Style(theme=theme)
        
        self.title(title)
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Configure modern styles
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("TButton", padding=6, relief="flat")
        self.style.configure("TEntry", padding=5)
        self.style.configure("TLabelframe", padding=10)
        self.style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Create UI
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
        
        # Observer pattern support
        self._observable = GUIObservable()
    
    def _create_header(self) -> None:
        """Create the modern header with search and theme toggle."""
        header_frame = tb.Frame(self, bootstyle="primary")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.columnconfigure(1, weight=1)
        
        # Title label
        title_label = tb.Label(
            header_frame,
            text="IP Definition Program",
            font=("Segoe UI", 16, "bold"),
            foreground="white",
            bootstyle="primary"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=(10, 20))
        
        # Search frame
        search_frame = tb.Frame(header_frame)
        search_frame.grid(row=0, column=1, sticky="ew", padx=20)
        search_frame.columnconfigure(0, weight=1)
        
        self.search_var = tb.StringVar()
        search_entry = tb.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            bootstyle="secondary"
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_entry.bind("<Return>", lambda e: self._on_search())
        
        search_button = tb.Button(
            search_frame,
            text="Analyze",
            command=self._on_search,
            bootstyle="primary-outline"
        )
        search_button.grid(row=0, column=1, sticky="e")
        
        # Theme toggle in header
        theme_frame = tb.Frame(header_frame)
        theme_frame.grid(row=0, column=2, sticky="e")
        
        self.theme_var = tb.StringVar(value="Dark Theme")
        theme_button = tb.Button(
            theme_frame,
            textvariable=self.theme_var,
            command=self._toggle_theme,
            bootstyle="secondary-outline"
        )
        theme_button.pack(side="right", padx=(0, 10))
    
    def _create_main_content(self) -> None:
        """Create the modern main content with sidebar and main area."""
        main_frame = tb.Frame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Sidebar with quick actions
        sidebar = tb.Labelframe(main_frame, text="Quick Actions", padding=10)
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        
        actions = [
            ("Public IP", self._get_public_ip),
            ("Local IP", self._get_local_ip),
            ("IPv4 Examples", self._show_ipv4_examples),
            ("IPv6 Examples", self._show_ipv6_examples),
            ("Clear Output", self._clear_output),
        ]
        
        for text, command in actions:
            btn = tb.Button(
                sidebar,
                text=f"  {text}",
                command=command,
                bootstyle="secondary",
                width=18,
                padding=5
            )
            btn.pack(fill="x", pady=5, padx=5)
        
        # Main content area
        content_frame = tb.Frame(main_frame)
        content_frame.grid(row=0, column=1, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        self._setup_results_area(content_frame)
    
    def _setup_results_area(self, parent) -> None:
        """Set up the results display area."""
        results_frame = tb.Labelframe(parent, text="Analysis Results", padding=10)
        results_frame.grid(row=0, column=0, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Scrollable text area using standard tk with modern styling
        self.result_frame = tk.Frame(results_frame)
        self.result_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(0, weight=1)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.result_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Text widget
        self.result_text = tk.Text(
            self.result_frame,
            wrap="word",
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set,
            bg="#f8f9fa",
            fg="#333",
            relief="flat",
            borderwidth=1
        )
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.result_text.yview)
        
        # Configure text tags
        self.result_text.tag_configure("header", foreground="#0d6efd", font=("Consolas", 9, "bold"))
        self.result_text.tag_configure("success", foreground="#198754", font=("Consolas", 9))
        self.result_text.tag_configure("error", foreground="#dc3545", font=("Consolas", 9))
        self.result_text.tag_configure("info", foreground="#6610f2", font=("Consolas", 9))
        self.result_text.tag_configure("default", font=("Consolas", 9))
        
        # Make read-only
        self.result_text.config(state="disabled")
    
    def _create_status_bar(self) -> None:
        """Create the modern status bar."""
        self.status_frame = tb.Frame(self)
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tb.StringVar(value="Ready")
        status_label = tb.Label(
            self.status_frame,
            textvariable=self.status_var,
            foreground="#6c757d",
            font=("Segoe UI", 9)
        )
        status_label.grid(row=0, column=0, sticky="w")
        
        # Status indicator
        self.status_indicator = tb.Label(
            self.status_frame,
            text="●",
            foreground="#198754",
            font=("Segoe UI", 10)
        )
        self.status_indicator.grid(row=0, column=1, padx=(10, 0))
    
    def _toggle_theme(self) -> None:
        """Toggle between dark and light themes."""
        # Available themes
        themes = ["darkly", "cyborg", "superhero", "flatly", "cosmo", "lumen", "pulse"]
        
        try:
            # Get current theme from style
            current_theme = self.style.theme_use()
            current_index = themes.index(current_theme)
        except ValueError:
            current_index = 0
        
        # Calculate next theme
        next_theme = themes[(current_index + 1) % len(themes)]
        
        # Apply new theme
        self.style.theme_use(next_theme)
        
        # Update button text
        dark_themes = ["darkly", "cyborg", "superhero"]
        if next_theme in dark_themes:
            self.theme_var.set("Light Theme")
        else:
            self.theme_var.set("Dark Theme")
        
        self.status_var.set(f"Theme: {next_theme}")
    
    def _on_search(self) -> None:
        """Handle search analysis."""
        ip_address = self.search_var.get().strip()
        if ip_address:
            self.status_var.set(f"Analyzing: {ip_address}")
            self.notify_observers({"type": "analyze", "ip": ip_address})
    
    def _get_public_ip(self) -> None:
        """Get public IP - to be implemented by subclass."""
        self.status_var.set("Fetching public IP...")
        self.notify_observers({"type": "public_ip"})
    
    def _get_local_ip(self) -> None:
        """Get local IP - to be implemented by subclass."""
        self.status_var.set("Getting local IP...")
        self.notify_observers({"type": "local_ip"})
    
    def _show_ipv4_examples(self) -> None:
        """Show IPv4 examples - to be implemented by subclass."""
        self.notify_observers({"type": "ipv4_examples"})
    
    def _show_ipv6_examples(self) -> None:
        """Show IPv6 examples - to be implemented by subclass."""
        self.notify_observers({"type": "ipv6_examples"})
    
    def _clear_output(self) -> None:
        """Clear the output display."""
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")
        self.status_var.set("Output cleared")
    
    def append_result(self, text: str, tag: str = "default") -> None:
        """Append text to the results display."""
        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, text, tag)
        self.result_text.config(state="disabled")
        self.result_text.see(tk.END)
    
    def add_observer(self, observer: GUIObserver) -> None:
        """Add a GUI observer."""
        self._observable.add_observer(observer)
    
    def remove_observer(self, observer: GUIObserver) -> None:
        """Remove a GUI observer."""
        self._observable.remove_observer(observer)
    
    def notify_observers(self, data: Any = None) -> None:
        """Notify all observers."""
        self._observable.notify_observers(data)

"""
Results view component for displaying IP analysis results.
"""

from typing import Any
import tkinter as tk
from tkinter import ttk


class ResultsView(ttk.Frame):
    """
    View for displaying IP analysis results.
    
    Provides a scrollable text area for showing detailed IP analysis
    results with color-coded formatting.
    """
    
    def __init__(self, parent: tk.Widget, controller: Any = None):
        """
        Initialize the results view.
        
        Args:
            parent: Parent widget
            controller: Controller instance
        """
        super().__init__(parent)
        self._controller = controller
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the results display UI."""
        # Results frame
        results_frame = ttk.LabelFrame(self, text="Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable text area
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self._results_text = tk.Text(
            text_frame,
            yscrollcommand=scrollbar.set,
            wrap="word",
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#333",
            relief="flat",
            borderwidth=1
        )
        scrollbar.config(command=self._results_text.yview)
        
        self._results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for color coding
        self._results_text.tag_configure("header", foreground="#0d6efd", font=("Consolas", 9, "bold"))
        self._results_text.tag_configure("success", foreground="#198754", font=("Consolas", 9))
        self._results_text.tag_configure("error", foreground="#dc3545", font=("Consolas", 9))
        self._results_text.tag_configure("info", foreground="#6610f2", font=("Consolas", 9))
        self._results_text.tag_configure("default", font=("Consolas", 9))
        
        # Make it read-only
        self._results_text.config(state="disabled")
    
    def append_result(self, text: str, tag: str = "default") -> None:
        """Append text to the results display with the specified tag."""
        self._results_text.config(state="normal")
        self._results_text.insert(tk.END, text, tag)
        self._results_text.config(state="disabled")
        self._results_text.see(tk.END)
    
    def clear_results(self) -> None:
        """Clear all results from the display."""
        self._results_text.config(state="normal")
        self._results_text.delete(1.0, tk.END)
        self._results_text.config(state="disabled")
    
    def update_view(self, data: Any) -> None:
        """Update the view with new data."""
        if data and data.get("type") == "results":
            self.append_result(data.get("text", ""), data.get("tag", "default"))

"""
Cashbook Card component for the Cashbook Dashboard application.

This module contains the CashbookCard class that displays individual
cashbook information with name, date, entry count, and interactive features
including hover effects and click handling.
"""

import customtkinter as ctk
from datetime import datetime
from typing import Callable, Optional
try:
    from models import Cashbook
except ImportError:
    from .models import Cashbook


class CashbookCard(ctk.CTkFrame):
    """
    Individual cashbook display card component.
    
    This card displays cashbook information including name, creation date,
    entry count, and category. It provides hover effects and click handling
    to open the cashbook detail view.
    """
    
    def __init__(
        self, 
        parent, 
        cashbook_data: Cashbook, 
        on_click_callback: Callable[[str], None],
        on_context_menu_callback: Optional[Callable[[str, int, int], None]] = None,
        **kwargs
    ):
        """
        Initialize the cashbook card.
        
        Args:
            parent: Parent widget
            cashbook_data: Cashbook object containing the data to display
            on_click_callback: Callback function called when card is clicked
                              Should accept cashbook_id as parameter
            on_context_menu_callback: Optional callback for right-click context menu
                                    Should accept (cashbook_id, x, y) parameters
            **kwargs: Additional arguments passed to CTkFrame
        """
        # Set default styling for the cashbook card
        default_kwargs = {
            'width': 250,
            'height': 150,
            'corner_radius': 10,
            'border_width': 1,
            'border_color': ("gray80", "gray25"),
            'fg_color': ("white", "gray20"),
            'cursor': 'hand2'
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)
        
        self.cashbook_data = cashbook_data
        self.on_click_callback = on_click_callback
        self.on_context_menu_callback = on_context_menu_callback
        self.grid_propagate(False)  # Maintain fixed size
        
        # Store original colors for hover effects
        self.original_fg_color = self.cget("fg_color")
        self.original_border_color = self.cget("border_color")
        
        self.setup_ui()
        self.setup_events()
    
    def setup_ui(self):
        """Set up the UI elements of the cashbook card."""
        # Configure grid for layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header area
        self.grid_rowconfigure(1, weight=1)  # Content area
        self.grid_rowconfigure(2, weight=0)  # Footer area
        
        # Header section with cashbook name and icon
        self.create_header_section()
        
        # Content section with details
        self.create_content_section()
        
        # Footer section with category (if exists)
        self.create_footer_section()
    
    def create_header_section(self):
        """Create the header section with cashbook name and visual indicator."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # Cashbook name (truncated if too long)
        display_name = self.cashbook_data.name
        if len(display_name) > 20:
            display_name = display_name[:17] + "..."
        
        self.name_label = ctk.CTkLabel(
            header_frame,
            text=display_name,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        self.name_label.grid(row=0, column=0, sticky="w")
        
        # Visual indicator (colored circle based on icon_color)
        self.color_indicator = ctk.CTkLabel(
            header_frame,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color=self.cashbook_data.icon_color,
            width=20
        )
        self.color_indicator.grid(row=0, column=1, sticky="e", padx=(5, 0))
    
    def create_content_section(self):
        """Create the content section with cashbook details."""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Creation date
        date_str = self.format_date(self.cashbook_data.created_date)
        self.date_label = ctk.CTkLabel(
            content_frame,
            text=f"Created: {date_str}",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40"),
            anchor="w"
        )
        self.date_label.grid(row=0, column=0, sticky="w", pady=(0, 3))
        
        # Entry count
        entry_text = f"{self.cashbook_data.entry_count} "
        entry_text += "entry" if self.cashbook_data.entry_count == 1 else "entries"
        
        self.entry_label = ctk.CTkLabel(
            content_frame,
            text=entry_text,
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40"),
            anchor="w"
        )
        self.entry_label.grid(row=1, column=0, sticky="w", pady=3)
        
        # Total amount (if there are entries)
        if self.cashbook_data.entry_count > 0:
            amount_text = f"Total: ${self.cashbook_data.total_amount:.2f}"
            self.amount_label = ctk.CTkLabel(
                content_frame,
                text=amount_text,
                font=ctk.CTkFont(size=12),
                text_color=("gray60", "gray40"),
                anchor="w"
            )
            self.amount_label.grid(row=2, column=0, sticky="w", pady=3)
        
        # Last modified (if different from created date)
        if self.cashbook_data.last_modified.date() != self.cashbook_data.created_date.date():
            modified_str = self.format_date(self.cashbook_data.last_modified)
            self.modified_label = ctk.CTkLabel(
                content_frame,
                text=f"Modified: {modified_str}",
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray50"),
                anchor="w"
            )
            self.modified_label.grid(row=3, column=0, sticky="w", pady=(3, 0))
    
    def create_footer_section(self):
        """Create the footer section with category information."""
        if self.cashbook_data.category:
            footer_frame = ctk.CTkFrame(self, fg_color="transparent")
            footer_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(5, 15))
            footer_frame.grid_columnconfigure(0, weight=1)
            
            # Category badge
            category_text = self.cashbook_data.category
            if len(category_text) > 15:
                category_text = category_text[:12] + "..."
            
            self.category_label = ctk.CTkLabel(
                footer_frame,
                text=f"📁 {category_text}",
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray50"),
                anchor="w"
            )
            self.category_label.grid(row=0, column=0, sticky="w")
    
    def format_date(self, date: datetime) -> str:
        """
        Format a date for display in the card.
        
        Args:
            date: datetime object to format
            
        Returns:
            Formatted date string
        """
        now = datetime.now()
        days_diff = (now.date() - date.date()).days
        
        if days_diff == 0:
            return "Today"
        elif days_diff == 1:
            return "Yesterday"
        elif days_diff < 7:
            return f"{days_diff} days ago"
        elif days_diff < 30:
            weeks = days_diff // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days_diff < 365:
            return date.strftime("%b %d")
        else:
            return date.strftime("%b %d, %Y")
    
    def setup_events(self):
        """Set up event handlers for the card."""
        # Bind click events to the card and all child widgets
        self.bind_click_events(self)
        
        # Bind hover events for visual feedback
        self.bind_hover_events(self)
        
        # Bind right-click for context menu if callback provided
        if self.on_context_menu_callback:
            self.bind_context_menu_events(self)
    
    def bind_click_events(self, widget):
        """
        Recursively bind click events to widget and all children.
        
        Args:
            widget: Widget to bind events to
        """
        widget.bind("<Button-1>", self.handle_click)
        
        # Bind to all child widgets recursively
        for child in widget.winfo_children():
            self.bind_click_events(child)
    
    def bind_hover_events(self, widget):
        """
        Recursively bind hover events to widget and all children.
        
        Args:
            widget: Widget to bind events to
        """
        widget.bind("<Enter>", self.handle_hover_enter)
        widget.bind("<Leave>", self.handle_hover_leave)
        
        # Bind to all child widgets recursively
        for child in widget.winfo_children():
            self.bind_hover_events(child)
    
    def bind_context_menu_events(self, widget):
        """
        Recursively bind context menu events to widget and all children.
        
        Args:
            widget: Widget to bind events to
        """
        widget.bind("<Button-3>", self.handle_context_menu)  # Right-click
        
        # Bind to all child widgets recursively
        for child in widget.winfo_children():
            self.bind_context_menu_events(child)
    
    def handle_click(self, event=None):
        """
        Handle click events to open cashbook detail view.
        
        Args:
            event: Tkinter event object (optional)
        """
        if self.on_click_callback:
            self.on_click_callback(self.cashbook_data.id)
    
    def handle_hover_enter(self, event=None):
        """
        Handle mouse enter events for hover effect.
        
        Args:
            event: Tkinter event object (optional)
        """
        # Change card appearance on hover
        self.configure(
            fg_color=("gray95", "gray25"),
            border_color=self.cashbook_data.icon_color
        )
        
        # Slightly brighten the text colors
        if hasattr(self, 'name_label'):
            self.name_label.configure(text_color=self.cashbook_data.icon_color)
    
    def handle_hover_leave(self, event=None):
        """
        Handle mouse leave events to restore normal appearance.
        
        Args:
            event: Tkinter event object (optional)
        """
        # Restore original appearance
        self.configure(
            fg_color=self.original_fg_color,
            border_color=self.original_border_color
        )
        
        # Restore original text colors
        if hasattr(self, 'name_label'):
            self.name_label.configure(text_color=("gray10", "gray90"))
    
    def handle_context_menu(self, event):
        """
        Handle right-click context menu events.
        
        Args:
            event: Tkinter event object containing click coordinates
        """
        if self.on_context_menu_callback:
            # Convert widget coordinates to screen coordinates
            x = self.winfo_rootx() + event.x
            y = self.winfo_rooty() + event.y
            self.on_context_menu_callback(self.cashbook_data.id, x, y)
    
    def update_display(self, cashbook_data: Optional[Cashbook] = None):
        """
        Update the card display with new cashbook data.
        
        Args:
            cashbook_data: Optional new cashbook data. If None, refreshes current data.
        """
        if cashbook_data:
            self.cashbook_data = cashbook_data
        
        # Clear existing content
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate UI with updated data
        self.setup_ui()
        self.setup_events()
"""
Create Cashbook Card component for the Cashbook Dashboard application.

This module contains the CreateCashbookCard class that provides a special
card interface for creating new cashbooks with a + icon and creation dialog.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional
import re


class CreateCashbookCard(ctk.CTkFrame):
    """
    Special card component for creating new cashbooks.
    
    This card displays a + icon and "Create new cashbook" text, and when
    clicked opens a dialog for cashbook creation with form validation.
    """
    
    def __init__(self, parent, on_create_callback: Callable[[str, str, str], None], **kwargs):
        """
        Initialize the create cashbook card.
        
        Args:
            parent: Parent widget
            on_create_callback: Callback function called when a cashbook is created
                               Should accept (name, description, category) parameters
            **kwargs: Additional arguments passed to CTkFrame
        """
        # Set default styling for the create card
        default_kwargs = {
            'width': 250,
            'height': 150,
            'corner_radius': 10,
            'border_width': 2,
            'border_color': ("gray70", "gray30"),
            'fg_color': ("gray95", "gray15"),
            'cursor': 'hand2'
        }
        default_kwargs.update(kwargs)
        
        super().__init__(parent, **default_kwargs)
        
        self.on_create_callback = on_create_callback
        self.grid_propagate(False)  # Maintain fixed size
        
        self.setup_ui()
        self.setup_events()
    
    def setup_ui(self):
        """Set up the UI elements of the create card."""
        # Configure grid for centering content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main container for centered content
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="")
        
        # Plus icon
        self.plus_icon = ctk.CTkLabel(
            content_frame,
            text="＋",  # Using full-width plus sign for better visibility
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=("gray60", "gray50")
        )
        self.plus_icon.pack(pady=(10, 5))
        
        # Create new cashbook text
        self.create_label = ctk.CTkLabel(
            content_frame,
            text="Create new cashbook",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray70", "gray40")
        )
        self.create_label.pack(pady=(0, 10))
    
    def setup_events(self):
        """Set up event handlers for the card."""
        # Bind click events to all components
        self.bind("<Button-1>", self.handle_click)
        self.plus_icon.bind("<Button-1>", self.handle_click)
        self.create_label.bind("<Button-1>", self.handle_click)
        
        # Bind hover events for visual feedback
        self.bind("<Enter>", self.on_hover_enter)
        self.bind("<Leave>", self.on_hover_leave)
        self.plus_icon.bind("<Enter>", self.on_hover_enter)
        self.plus_icon.bind("<Leave>", self.on_hover_leave)
        self.create_label.bind("<Enter>", self.on_hover_enter)
        self.create_label.bind("<Leave>", self.on_hover_leave)
    
    def handle_click(self, event=None):
        """Handle click events to open the cashbook creation dialog."""
        self.show_creation_dialog()
    
    def on_hover_enter(self, event=None):
        """Handle mouse enter events for hover effect."""
        self.configure(
            fg_color=("gray90", "gray20"),
            border_color=("blue", "lightblue")
        )
        self.plus_icon.configure(text_color=("blue", "lightblue"))
        self.create_label.configure(text_color=("blue", "lightblue"))
    
    def on_hover_leave(self, event=None):
        """Handle mouse leave events to restore normal appearance."""
        self.configure(
            fg_color=("gray95", "gray15"),
            border_color=("gray70", "gray30")
        )
        self.plus_icon.configure(text_color=("gray60", "gray50"))
        self.create_label.configure(text_color=("gray70", "gray40"))
    
    def show_creation_dialog(self):
        """Show the cashbook creation dialog with form validation."""
        dialog = CashbookCreationDialog(
            parent=self.winfo_toplevel(),
            on_create_callback=self.on_create_callback
        )
        dialog.show()


class CashbookCreationDialog:
    """
    Dialog for creating new cashbooks with form validation.
    
    This dialog provides input fields for cashbook name (required),
    description (optional), and category (optional) with proper validation.
    """
    
    def __init__(self, parent, on_create_callback: Callable[[str, str, str], None]):
        """
        Initialize the creation dialog.
        
        Args:
            parent: Parent window
            on_create_callback: Callback function for when cashbook is created
        """
        self.parent = parent
        self.on_create_callback = on_create_callback
        self.dialog = None
        
        # Predefined categories for selection
        self.categories = [
            "Personal",
            "Business", 
            "Travel",
            "Education",
            "Healthcare",
            "Entertainment",
            "Other"
        ]
    
    def show(self):
        """Show the creation dialog."""
        # Create toplevel window
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Create New Cashbook")
        self.dialog.geometry("400x450")  # Increased height to ensure buttons are visible
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog on parent window
        self.center_dialog()
        
        self.setup_dialog_ui()
        
        # Focus on name entry
        self.name_entry.focus()
    
    def center_dialog(self):
        """Center the dialog on the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate dialog position
        dialog_width = 400
        dialog_height = 450
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def setup_dialog_ui(self):
        """Set up the dialog UI elements."""
        # Configure grid
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self.dialog,
            text="Create New Cashbook",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 30), padx=20, sticky="w")
        
        # Name field (required)
        name_label = ctk.CTkLabel(
            self.dialog,
            text="Cashbook Name *",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.grid(row=1, column=0, pady=(0, 5), padx=20, sticky="ew")
        
        self.name_entry = ctk.CTkEntry(
            self.dialog,
            placeholder_text="Enter cashbook name...",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.name_entry.grid(row=2, column=0, pady=(0, 15), padx=20, sticky="ew")
        
        # Description field (optional)
        desc_label = ctk.CTkLabel(
            self.dialog,
            text="Description (Optional)",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        desc_label.grid(row=3, column=0, pady=(0, 5), padx=20, sticky="ew")
        
        self.desc_entry = ctk.CTkEntry(
            self.dialog,
            placeholder_text="Enter description...",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.desc_entry.grid(row=4, column=0, pady=(0, 15), padx=20, sticky="ew")
        
        # Category field (optional)
        category_label = ctk.CTkLabel(
            self.dialog,
            text="Category (Optional)",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        category_label.grid(row=5, column=0, pady=(0, 5), padx=20, sticky="ew")
        
        self.category_combo = ctk.CTkComboBox(
            self.dialog,
            values=self.categories,
            font=ctk.CTkFont(size=12),
            height=35,
            state="readonly",
            command=self.on_category_change
        )
        self.category_combo.set("")  # No default selection
        self.category_combo.grid(row=6, column=0, pady=(0, 15), padx=20, sticky="ew")
        
        # Custom category field (initially hidden)
        self.custom_category_label = ctk.CTkLabel(
            self.dialog,
            text="Custom Category",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        
        self.custom_category_entry = ctk.CTkEntry(
            self.dialog,
            placeholder_text="Enter custom category...",
            font=ctk.CTkFont(size=12),
            height=35
        )
        
        # Initially hide custom category widgets
        self.custom_category_widgets_visible = False
        
        # Error label for validation messages
        self.error_label = ctk.CTkLabel(
            self.dialog,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="red",
            anchor="w"
        )
        self.error_label.grid(row=9, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        self.buttons_frame.grid(row=10, column=0, pady=(0, 20), padx=20, sticky="ew")
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.buttons_frame,
            text="Cancel",
            command=self.cancel_creation,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90"),
            border_color=("gray70", "gray30"),
            hover_color=("gray90", "gray20"),
            height=35
        )
        self.cancel_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        # Create button
        self.create_button = ctk.CTkButton(
            self.buttons_frame,
            text="Create Cashbook",
            command=self.create_cashbook,
            height=35
        )
        self.create_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        # Bind Enter key to create button
        self.dialog.bind("<Return>", lambda e: self.create_cashbook())
        self.dialog.bind("<Escape>", lambda e: self.cancel_creation())
    
    def on_category_change(self, selected_category):
        """
        Handle category selection changes.
        
        Args:
            selected_category: The selected category value
        """
        if selected_category == "Other":
            self.show_custom_category_field()
        else:
            self.hide_custom_category_field()
    
    def show_custom_category_field(self):
        """Show the custom category input field."""
        if not self.custom_category_widgets_visible:
            # Show the custom category label and entry in separate rows
            self.custom_category_label.grid(row=7, column=0, pady=(0, 5), padx=20, sticky="ew")
            self.custom_category_entry.grid(row=8, column=0, pady=(0, 15), padx=20, sticky="ew")
            
            # Move error label and buttons down
            self.error_label.grid(row=9, column=0, pady=(0, 10), padx=20, sticky="ew")
            self.buttons_frame.grid(row=10, column=0, pady=(0, 20), padx=20, sticky="ew")
            
            # Update dialog size to accommodate new field
            self.dialog.geometry("400x500")
            
            self.custom_category_widgets_visible = True
            
            # Focus on custom category entry
            self.custom_category_entry.focus()
    
    def hide_custom_category_field(self):
        """Hide the custom category input field."""
        if self.custom_category_widgets_visible:
            # Hide the custom category widgets
            self.custom_category_label.grid_remove()
            self.custom_category_entry.grid_remove()
            
            # Move error label and buttons back up
            self.error_label.grid(row=9, column=0, pady=(0, 10), padx=20, sticky="ew")
            self.buttons_frame.grid(row=10, column=0, pady=(0, 20), padx=20, sticky="ew")
            
            # Reset dialog size
            self.dialog.geometry("400x450")
            
            self.custom_category_widgets_visible = False
            
            # Clear custom category entry
            self.custom_category_entry.delete(0, 'end')
    
    def validate_form(self) -> tuple[bool, str]:
        """
        Validate the form inputs.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        name = self.name_entry.get().strip()
        
        # Check if name is provided
        if not name:
            return False, "Cashbook name is required"
        
        # Check name length
        if len(name) < 2:
            return False, "Cashbook name must be at least 2 characters long"
        
        if len(name) > 50:
            return False, "Cashbook name must be less than 50 characters"
        
        # Check for valid characters (allow letters, numbers, spaces, and common punctuation)
        if not re.match(r'^[a-zA-Z0-9\s\-_.,()]+$', name):
            return False, "Cashbook name contains invalid characters"
        
        # Check description length if provided
        description = self.desc_entry.get().strip()
        if description and len(description) > 200:
            return False, "Description must be less than 200 characters"
        
        # Check custom category length if "Other" is selected and custom category is provided
        category = self.category_combo.get().strip()
        if category == "Other":
            custom_category = self.custom_category_entry.get().strip()
            if custom_category and len(custom_category) > 50:
                return False, "Custom category must be less than 50 characters"
            if custom_category and not re.match(r'^[a-zA-Z0-9\s\-_.,()]+$', custom_category):
                return False, "Custom category contains invalid characters"
        
        return True, ""
    
    def create_cashbook(self):
        """Handle cashbook creation with validation."""
        # Validate form
        is_valid, error_message = self.validate_form()
        
        if not is_valid:
            self.show_error(error_message)
            return
        
        # Clear any previous errors
        self.clear_error()
        
        # Get form values
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        category = self.category_combo.get().strip()
        
        # Handle custom category
        if category == "Other":
            custom_category = self.custom_category_entry.get().strip()
            if custom_category:
                category = custom_category
            # If no custom category entered, keep "Other" as the category
        
        try:
            # Call the callback to create the cashbook
            self.on_create_callback(name, description, category)
            
            # Close dialog on success
            self.dialog.destroy()
            
        except Exception as e:
            # Show error if creation fails
            self.show_error(f"Failed to create cashbook: {str(e)}")
    
    def cancel_creation(self):
        """Handle dialog cancellation."""
        self.dialog.destroy()
    
    def show_error(self, message: str):
        """
        Show an error message in the dialog.
        
        Args:
            message: Error message to display
        """
        self.error_label.configure(text=message)
    
    def clear_error(self):
        """Clear any displayed error message."""
        self.error_label.configure(text="")
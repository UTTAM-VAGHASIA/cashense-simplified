"""
Cashbook Detail View for the Cashbook Dashboard application.

This module contains the CashbookDetailView class that provides the detailed
view for a specific cashbook, including expense entries, navigation controls,
and breadcrumb navigation back to the dashboard.
"""

import customtkinter as ctk
from typing import Optional, Callable
from datetime import datetime
try:
    from models import Cashbook
    from cashbook_manager import CashbookManager
    from theme_manager import theme, animations, icons
except ImportError:
    from .models import Cashbook
    from .cashbook_manager import CashbookManager
    from .theme_manager import theme, animations, icons


class CashbookDetailView(ctk.CTkFrame):
    """
    Detailed view for a specific cashbook.
    
    This view displays:
    - Breadcrumb navigation back to dashboard
    - Cashbook header with name, category, and stats
    - Expense entries list (placeholder for now)
    - Action buttons for adding entries
    """
    
    def __init__(
        self, 
        parent, 
        cashbook_manager: CashbookManager,
        cashbook_id: str,
        on_back_callback: Callable[[], None],
        **kwargs
    ):
        """
        Initialize the cashbook detail view.
        
        Args:
            parent: Parent widget
            cashbook_manager: CashbookManager instance for data operations
            cashbook_id: ID of the cashbook to display
            on_back_callback: Callback function to return to dashboard
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, **kwargs)
        
        self.cashbook_manager = cashbook_manager
        self.cashbook_id = cashbook_id
        self.on_back_callback = on_back_callback
        self.cashbook_data = None
        
        # Configure grid weights for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Main content area expands
        
        # Load cashbook data
        self.load_cashbook_data()
        
        if self.cashbook_data:
            self.setup_layout()
        else:
            self.show_error_state()
    
    def load_cashbook_data(self):
        """Load the cashbook data from the manager."""
        try:
            self.cashbook_data = self.cashbook_manager.get_cashbook(self.cashbook_id)
        except Exception as e:
            print(f"Error loading cashbook {self.cashbook_id}: {e}")
            self.cashbook_data = None
    
    def setup_layout(self):
        """Set up the main layout structure of the detail view."""
        # Breadcrumb navigation
        self.create_breadcrumb_section()
        
        # Cashbook header with details
        self.create_header_section()
        
        # Main content area (entries list)
        self.create_main_content_area()
        
        # Footer with actions
        self.create_footer_section()
    
    def create_breadcrumb_section(self):
        """Create the breadcrumb navigation section."""
        breadcrumb_frame = ctk.CTkFrame(
            self,
            height=50,
            corner_radius=0,
            fg_color=(theme.DARK_THEME['surface'], theme.DARK_THEME['surface'])
        )
        breadcrumb_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        breadcrumb_frame.grid_columnconfigure(1, weight=1)
        breadcrumb_frame.grid_propagate(False)
        
        # Back button
        button_style = theme.get_button_style('ghost')
        back_button = ctk.CTkButton(
            breadcrumb_frame,
            text="← Dashboard",
            command=self.handle_back_navigation,
            width=100,
            height=30,
            **{k: v for k, v in button_style.items() if k not in ['width', 'height']}
        )
        back_button.grid(row=0, column=0, sticky="w", padx=theme.SPACING['lg'], pady=theme.SPACING['md'])
        
        # Breadcrumb text
        breadcrumb_text = f"Dashboard > {self.cashbook_data.name}"
        if len(breadcrumb_text) > 50:
            breadcrumb_text = f"Dashboard > {self.cashbook_data.name[:40]}..."
        
        breadcrumb_label = ctk.CTkLabel(
            breadcrumb_frame,
            text=breadcrumb_text,
            font=theme.create_font('sm'),
            text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary']),
            anchor="w"
        )
        breadcrumb_label.grid(row=0, column=1, sticky="w", padx=theme.SPACING['md'], pady=theme.SPACING['md'])
    
    def create_header_section(self):
        """Create the cashbook header section with details and stats."""
        header_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=(theme.DARK_THEME['background'], theme.DARK_THEME['background'])
        )
        header_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Cashbook icon and category
        category_icon = icons.get_category_icon(self.cashbook_data.category or 'other')
        cashbook_color = theme.get_cashbook_color(self.cashbook_data.id)
        
        icon_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        icon_frame.grid(row=0, column=0, sticky="w", padx=theme.SPACING['lg'], pady=theme.SPACING['lg'])
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=category_icon,
            font=theme.create_font('heading'),
            text_color=(cashbook_color, cashbook_color)
        )
        icon_label.pack()
        
        # Cashbook details
        details_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        details_frame.grid(row=0, column=1, sticky="ew", padx=theme.SPACING['md'], pady=theme.SPACING['lg'])
        details_frame.grid_columnconfigure(0, weight=1)
        
        # Cashbook name
        name_label = ctk.CTkLabel(
            details_frame,
            text=self.cashbook_data.name,
            font=theme.create_font('heading', 'bold'),
            text_color=(theme.DARK_THEME['text_primary'], theme.DARK_THEME['text_primary']),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w", pady=(0, theme.SPACING['sm']))
        
        # Category and creation date
        info_text = f"{self.cashbook_data.category or 'Uncategorized'} • Created {self.format_date(self.cashbook_data.created_date)}"
        info_label = ctk.CTkLabel(
            details_frame,
            text=info_text,
            font=theme.create_font('sm'),
            text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary']),
            anchor="w"
        )
        info_label.grid(row=1, column=0, sticky="w", pady=(0, theme.SPACING['md']))
        
        # Stats row
        stats_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew")
        
        # Entry count
        entry_text = f"{self.cashbook_data.entry_count} entries"
        entry_label = ctk.CTkLabel(
            stats_frame,
            text=f"📝 {entry_text}",
            font=theme.create_font('sm'),
            text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary'])
        )
        entry_label.pack(side="left", padx=(0, theme.SPACING['lg']))
        
        # Total amount
        if self.cashbook_data.entry_count > 0:
            amount_text = f"${self.cashbook_data.total_amount:.2f}"
            amount_color = theme.DARK_THEME['success'] if self.cashbook_data.total_amount >= 0 else theme.DARK_THEME['error']
            
            amount_label = ctk.CTkLabel(
                stats_frame,
                text=f"💰 {amount_text}",
                font=theme.create_font('sm', 'medium'),
                text_color=(amount_color, amount_color)
            )
            amount_label.pack(side="left", padx=(0, theme.SPACING['lg']))
        
        # Last modified
        if self.cashbook_data.last_modified.date() != self.cashbook_data.created_date.date():
            modified_text = f"Updated {self.format_date(self.cashbook_data.last_modified)}"
            modified_label = ctk.CTkLabel(
                stats_frame,
                text=f"✏️ {modified_text}",
                font=theme.create_font('sm'),
                text_color=(theme.DARK_THEME['text_muted'], theme.DARK_THEME['text_muted'])
            )
            modified_label.pack(side="left")
    
    def create_main_content_area(self):
        """Create the main content area for expense entries."""
        # Scrollable frame for entries
        self.main_content = ctk.CTkScrollableFrame(
            self,
            corner_radius=theme.RADIUS['base'],
            fg_color=(theme.DARK_THEME['surface'], theme.DARK_THEME['surface'])
        )
        self.main_content.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Show entries or empty state
        if self.cashbook_data.entry_count > 0:
            self.show_entries_placeholder()
        else:
            self.show_empty_entries_state()
    
    def show_entries_placeholder(self):
        """Show placeholder content for expense entries."""
        # Header for entries section
        entries_header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        entries_header.pack(fill="x", padx=theme.SPACING['lg'], pady=(theme.SPACING['lg'], theme.SPACING['md']))
        
        entries_title = ctk.CTkLabel(
            entries_header,
            text=f"📋 Expense Entries ({self.cashbook_data.entry_count})",
            font=theme.create_font('lg', 'bold'),
            text_color=(theme.DARK_THEME['text_primary'], theme.DARK_THEME['text_primary']),
            anchor="w"
        )
        entries_title.pack(side="left")
        
        # Add entry button
        button_style = theme.get_button_style('primary')
        add_button = ctk.CTkButton(
            entries_header,
            text="+ Add Entry",
            command=self.handle_add_entry,
            width=100,
            height=30,
            **{k: v for k, v in button_style.items() if k not in ['width', 'height']}
        )
        add_button.pack(side="right")
        
        # Placeholder entries list
        for i in range(min(self.cashbook_data.entry_count, 5)):  # Show up to 5 placeholder entries
            self.create_placeholder_entry(i + 1)
        
        # Show more entries indicator if needed
        if self.cashbook_data.entry_count > 5:
            more_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
            more_frame.pack(fill="x", padx=theme.SPACING['lg'], pady=theme.SPACING['md'])
            
            more_label = ctk.CTkLabel(
                more_frame,
                text=f"... and {self.cashbook_data.entry_count - 5} more entries",
                font=theme.create_font('sm'),
                text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary'])
            )
            more_label.pack()
    
    def create_placeholder_entry(self, entry_number: int):
        """Create a placeholder entry item."""
        entry_frame = ctk.CTkFrame(
            self.main_content,
            fg_color=(theme.DARK_THEME['background'], theme.DARK_THEME['background']),
            corner_radius=theme.RADIUS['sm']
        )
        entry_frame.pack(fill="x", padx=theme.SPACING['lg'], pady=theme.SPACING['sm'])
        
        # Entry content
        content_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=theme.SPACING['md'], pady=theme.SPACING['md'])
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Entry icon
        entry_icon = ctk.CTkLabel(
            content_frame,
            text="💳",
            font=theme.create_font('lg')
        )
        entry_icon.grid(row=0, column=0, sticky="w", padx=(0, theme.SPACING['md']))
        
        # Entry details
        details_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        details_frame.grid(row=0, column=1, sticky="ew")
        details_frame.grid_columnconfigure(0, weight=1)
        
        # Entry description
        desc_label = ctk.CTkLabel(
            details_frame,
            text=f"Sample Expense Entry #{entry_number}",
            font=theme.create_font('base', 'medium'),
            text_color=(theme.DARK_THEME['text_primary'], theme.DARK_THEME['text_primary']),
            anchor="w"
        )
        desc_label.grid(row=0, column=0, sticky="w")
        
        # Entry date and category
        date_text = f"Today • Category {entry_number}"
        date_label = ctk.CTkLabel(
            details_frame,
            text=date_text,
            font=theme.create_font('sm'),
            text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary']),
            anchor="w"
        )
        date_label.grid(row=1, column=0, sticky="w", pady=(theme.SPACING['xs'], 0))
        
        # Entry amount
        amount_text = f"${(entry_number * 25.50):.2f}"
        amount_label = ctk.CTkLabel(
            content_frame,
            text=amount_text,
            font=theme.create_font('base', 'bold'),
            text_color=(theme.DARK_THEME['error'], theme.DARK_THEME['error'])
        )
        amount_label.grid(row=0, column=2, sticky="e", padx=(theme.SPACING['md'], 0))
    
    def show_empty_entries_state(self):
        """Show empty state when no entries exist."""
        empty_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        empty_frame.pack(expand=True, fill="both", padx=theme.SPACING['xl'], pady=theme.SPACING['xl'])
        
        # Empty state icon
        empty_icon = ctk.CTkLabel(
            empty_frame,
            text="📝",
            font=theme.create_font('heading')
        )
        empty_icon.pack(pady=(theme.SPACING['xl'], theme.SPACING['md']))
        
        # Empty state title
        empty_title = ctk.CTkLabel(
            empty_frame,
            text="No entries yet",
            font=theme.create_font('xl', 'bold'),
            text_color=(theme.DARK_THEME['text_primary'], theme.DARK_THEME['text_primary'])
        )
        empty_title.pack(pady=(0, theme.SPACING['sm']))
        
        # Empty state description
        empty_desc = ctk.CTkLabel(
            empty_frame,
            text="Start tracking your expenses by adding your first entry.\nYou can record purchases, bills, income, and more.",
            font=theme.create_font('base'),
            text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary']),
            justify="center"
        )
        empty_desc.pack(pady=(0, theme.SPACING['lg']))
        
        # Add first entry button
        button_style = theme.get_button_style('primary')
        add_button = ctk.CTkButton(
            empty_frame,
            text="+ Add First Entry",
            command=self.handle_add_entry,
            width=140,
            height=40,
            **{k: v for k, v in button_style.items() if k not in ['width', 'height']}
        )
        add_button.pack(pady=theme.SPACING['md'])
    
    def create_footer_section(self):
        """Create the footer section with action buttons."""
        footer_frame = ctk.CTkFrame(
            self,
            height=60,
            corner_radius=0,
            fg_color=(theme.DARK_THEME['surface'], theme.DARK_THEME['surface'])
        )
        footer_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_propagate(False)
        
        # Action buttons frame
        actions_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=theme.SPACING['lg'], pady=theme.SPACING['md'])
        
        # Add entry button
        button_style = theme.get_button_style('primary')
        add_entry_button = ctk.CTkButton(
            actions_frame,
            text="+ Add Entry",
            command=self.handle_add_entry,
            width=100,
            **{k: v for k, v in button_style.items() if k not in ['width', 'height']}
        )
        add_entry_button.pack(side="left", padx=(0, theme.SPACING['md']))
        
        # Settings button
        button_style = theme.get_button_style('ghost')
        settings_button = ctk.CTkButton(
            actions_frame,
            text="⚙️ Settings",
            command=self.handle_settings,
            width=100,
            **{k: v for k, v in button_style.items() if k not in ['width', 'height']}
        )
        settings_button.pack(side="left")
        
        # Status label
        status_label = ctk.CTkLabel(
            footer_frame,
            text=f"✅ Viewing {self.cashbook_data.name}",
            font=theme.create_font('sm'),
            text_color=(theme.DARK_THEME['text_muted'], theme.DARK_THEME['text_muted'])
        )
        status_label.pack(side="left", padx=theme.SPACING['lg'], pady=theme.SPACING['md'])
    
    def show_error_state(self):
        """Show error state when cashbook cannot be loaded."""
        # Configure for error display
        self.grid_rowconfigure(0, weight=1)
        
        error_frame = ctk.CTkFrame(self, fg_color="transparent")
        error_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        
        # Error icon
        error_icon = ctk.CTkLabel(
            error_frame,
            text="⚠️",
            font=theme.create_font('heading')
        )
        error_icon.pack(pady=(theme.SPACING['xl'], theme.SPACING['md']))
        
        # Error title
        error_title = ctk.CTkLabel(
            error_frame,
            text="Cashbook Not Found",
            font=theme.create_font('xl', 'bold'),
            text_color=(theme.DARK_THEME['error'], theme.DARK_THEME['error'])
        )
        error_title.pack(pady=(0, theme.SPACING['sm']))
        
        # Error description
        error_desc = ctk.CTkLabel(
            error_frame,
            text=f"The cashbook with ID '{self.cashbook_id}' could not be found.\nIt may have been deleted or corrupted.",
            font=theme.create_font('base'),
            text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary']),
            justify="center"
        )
        error_desc.pack(pady=(0, theme.SPACING['lg']))
        
        # Back to dashboard button
        button_style = theme.get_button_style('primary')
        back_button = ctk.CTkButton(
            error_frame,
            text="← Back to Dashboard",
            command=self.handle_back_navigation,
            width=160,
            **{k: v for k, v in button_style.items() if k not in ['width', 'height']}
        )
        back_button.pack(pady=theme.SPACING['md'])
    
    def format_date(self, date: datetime) -> str:
        """Format a date for display."""
        now = datetime.now()
        days_diff = (now.date() - date.date()).days
        
        if days_diff == 0:
            return "today"
        elif days_diff == 1:
            return "yesterday"
        elif days_diff < 7:
            return f"{days_diff} days ago"
        elif days_diff < 30:
            weeks = days_diff // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            return date.strftime("%B %d, %Y")
    
    def handle_back_navigation(self):
        """Handle navigation back to dashboard."""
        if self.on_back_callback:
            self.on_back_callback()
    
    def handle_add_entry(self):
        """Handle adding a new expense entry (placeholder)."""
        print(f"Add entry to cashbook: {self.cashbook_data.name}")
        # TODO: Implement entry creation dialog in future tasks
    
    def handle_settings(self):
        """Handle cashbook settings (placeholder)."""
        print(f"Settings for cashbook: {self.cashbook_data.name}")
        # TODO: Implement settings dialog in future tasks
    
    def refresh_view(self):
        """Refresh the view with updated data."""
        # Reload cashbook data
        self.load_cashbook_data()
        
        # Clear existing content
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate layout
        if self.cashbook_data:
            self.setup_layout()
        else:
            self.show_error_state()
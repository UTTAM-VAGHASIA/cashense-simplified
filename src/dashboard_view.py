"""
Dashboard View for the Cashbook Dashboard application.

This module contains the DashboardView class that provides the main
dashboard interface for managing cashbooks, replacing the simple
welcome screen with a modern card-based layout.
"""

import customtkinter as ctk
from typing import Optional, Callable
try:
    from cashbook_manager import CashbookManager, FileOperationError, DataCorruptionError
    from create_cashbook_card import CreateCashbookCard
    from cashbook_card import CashbookCard
    from theme_manager import theme, animations, icons
except ImportError:
    from .cashbook_manager import CashbookManager, FileOperationError, DataCorruptionError
    from .create_cashbook_card import CreateCashbookCard
    from .cashbook_card import CashbookCard
    from .theme_manager import theme, animations, icons


class DashboardView(ctk.CTkFrame):
    """
    Main dashboard view that displays cashbooks in a card-based layout.
    
    This view replaces the current welcome screen and provides:
    - Header section with "Recent cashbooks" title
    - Grid container for cashbook cards with responsive layout
    - Integration with CashbookManager for data operations
    """
    
    def __init__(self, parent, cashbook_manager: CashbookManager, **kwargs):
        """
        Initialize the dashboard view.
        
        Args:
            parent: Parent widget (typically the main window)
            cashbook_manager: CashbookManager instance for data operations
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, **kwargs)
        
        self.cashbook_manager = cashbook_manager
        self.parent = parent
        
        # Initialize responsive design attributes
        self.current_layout_mode = "desktop"
        self.cards_per_row = 2
        self.see_all_button = None
        self.see_all_frame = None
        
        # Configure grid weights for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Main content area expands
        
        self.setup_layout()
        self.refresh_cashbooks()
        
        # Bind to configure events for responsive design
        self.bind("<Configure>", self._on_frame_configure)
    
    def setup_layout(self):
        """Set up the main layout structure of the dashboard."""
        # Header section
        self.create_header_section()
        
        # Main content area (grid container)
        self.create_main_content_area()
        
        # Footer section (for future status/actions)
        self.create_footer_section()
    
    def create_header_section(self):
        """Create the enhanced header section with title and navigation."""
        header_frame = ctk.CTkFrame(
            self, 
            height=80, 
            corner_radius=0,
            fg_color=(theme.DARK_THEME['surface'], theme.DARK_THEME['surface'])
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_propagate(False)  # Maintain fixed height
        
        # Enhanced main title with icon
        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 Recent cashbooks",
            font=theme.create_font('title', 'bold'),
            text_color=(theme.DARK_THEME['text_primary'], theme.DARK_THEME['text_primary']),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=theme.SPACING['xl'], pady=theme.SPACING['lg'])
        
        self.header_frame = header_frame
    
    def create_main_content_area(self):
        """Create the main content area that will contain the cashbook grid."""
        # Scrollable frame for the grid content
        self.main_content = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            fg_color="transparent"
        )
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Configure grid for responsive layout
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(1, weight=1)
        
        # Grid container for cashbook cards
        self.create_cashbook_grid()
    
    def create_cashbook_grid(self):
        """Create the grid container for cashbook cards."""
        # Grid frame that will contain the cards
        self.grid_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.grid_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=20)
        
        # Configure responsive grid layout
        self.configure_grid_layout()
        
        # Track current layout mode for responsive design
        self.current_layout_mode = "desktop"  # desktop, tablet, mobile
        self.cards_per_row = 2  # Default for desktop
        
        # Store reference to see all button for dynamic updates
        self.see_all_button = None
    
    def create_footer_section(self):
        """Create the enhanced footer section for status and additional actions."""
        footer_frame = ctk.CTkFrame(
            self, 
            height=40, 
            corner_radius=0,
            fg_color=(theme.DARK_THEME['surface'], theme.DARK_THEME['surface'])
        )
        footer_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_propagate(False)  # Maintain fixed height
        
        # Enhanced status label with icon
        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="✅ Ready",
            font=theme.create_font('sm'),
            text_color=(theme.DARK_THEME['text_muted'], theme.DARK_THEME['text_muted'])
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=theme.SPACING['lg'], pady=theme.SPACING['md'])
        
        self.footer_frame = footer_frame
    
    def refresh_cashbooks(self):
        """Refresh the display of cashbooks in the grid with error handling."""
        try:
            # Clear existing grid content
            for widget in self.grid_frame.winfo_children():
                widget.destroy()
            
            # Clear see all button if it exists
            if hasattr(self, 'see_all_button') and self.see_all_button:
                try:
                    self.see_all_button.destroy()
                except:
                    pass
                self.see_all_button = None
            
            if hasattr(self, 'see_all_frame') and self.see_all_frame:
                try:
                    self.see_all_frame.destroy()
                except:
                    pass
                self.see_all_frame = None
            
            # Reconfigure grid layout for current window size
            self.configure_grid_layout()
            
            # Get recent cashbooks based on current layout capacity
            max_visible = self.calculate_max_visible_cashbooks() - 1  # -1 for create card
            
            try:
                recent_cashbooks = self.cashbook_manager.get_recent_cashbooks(limit=max_visible)
            except Exception as e:
                # Handle data loading errors
                self.show_data_error(str(e))
                return
            
            if not recent_cashbooks:
                # Show empty state
                self.show_empty_state()
            else:
                # Display cashbooks in grid
                self.display_cashbooks_grid(recent_cashbooks)
                
        except Exception as e:
            # Handle any unexpected errors during refresh
            self.show_data_error(f"Failed to refresh dashboard: {str(e)}")
    
    def show_data_error(self, error_message: str):
        """Show a data error state in the dashboard."""
        # Clear existing content
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        # Create error display
        error_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        error_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20, pady=40)
        
        # Enhanced error icon and message
        error_icon = ctk.CTkLabel(
            error_frame,
            text="⚠️",
            font=theme.create_font('heading')
        )
        error_icon.pack(pady=(theme.SPACING['xl'], theme.SPACING['md']))
        
        error_title = ctk.CTkLabel(
            error_frame,
            text="Data Loading Error",
            font=theme.create_font('xl', 'bold'),
            text_color=(theme.DARK_THEME['error'], theme.DARK_THEME['error'])
        )
        error_title.pack(pady=(0, theme.SPACING['sm']))
        
        error_subtitle = ctk.CTkLabel(
            error_frame,
            text=f"Unable to load cashbook data:\n{error_message}",
            font=theme.create_font('base'),
            text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary']),
            justify="center"
        )
        error_subtitle.pack(pady=(0, theme.SPACING['lg']))
        
        # Enhanced action buttons
        button_frame = ctk.CTkFrame(error_frame, fg_color="transparent")
        button_frame.pack(pady=theme.SPACING['md'])
        
        retry_style = theme.get_button_style('primary')
        retry_button = ctk.CTkButton(
            button_frame,
            text="🔄 Retry",
            command=self.refresh_cashbooks,
            **retry_style,
            width=100
        )
        retry_button.pack(side="left", padx=(0, theme.SPACING['md']))
        
        recovery_style = theme.get_button_style('ghost')
        recovery_button = ctk.CTkButton(
            button_frame,
            text="🔧 Recovery Info",
            command=self.show_recovery_info,
            **recovery_style,
            width=120
        )
        recovery_button.pack(side="left")
        
        # Update status with error icon
        self.update_status(f"❌ Error: {error_message}")
    
    def show_empty_state(self):
        """Display empty state when no cashbooks exist with helpful guidance."""
        # Check for any data recovery information
        recovery_info = self.cashbook_manager.get_error_recovery_info()
        
        # Add the create new cashbook card
        create_card = CreateCashbookCard(
            self.grid_frame,
            on_create_callback=self.handle_cashbook_creation
        )
        create_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add empty state message in the remaining space
        empty_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        empty_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=20, pady=40)
        
        # Enhanced empty state icon and message
        empty_icon = ctk.CTkLabel(
            empty_frame,
            text="📚",
            font=theme.create_font('heading')
        )
        empty_icon.pack(pady=(theme.SPACING['xl'], theme.SPACING['md']))
        
        empty_title = ctk.CTkLabel(
            empty_frame,
            text="No cashbooks yet",
            font=theme.create_font('xl', 'bold'),
            text_color=(theme.DARK_THEME['text_primary'], theme.DARK_THEME['text_primary'])
        )
        empty_title.pack(pady=(0, theme.SPACING['sm']))
        
        # Show different messages based on recovery status
        if recovery_info.get("has_backups", False):
            empty_subtitle = ctk.CTkLabel(
                empty_frame,
                text="Your data was recovered from a backup.\nCreate a new cashbook to get started.",
                font=theme.create_font('base'),
                text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary']),
                justify="center"
            )
            empty_subtitle.pack(pady=(0, theme.SPACING['md']))
            
            # Add enhanced recovery info button
            recovery_style = theme.get_button_style('ghost')
            recovery_button = ctk.CTkButton(
                empty_frame,
                text="🔧 View Recovery Info",
                command=self.show_recovery_info,
                **recovery_style,
                width=140
            )
            recovery_button.pack(pady=(0, theme.SPACING['md']))
        else:
            empty_subtitle = ctk.CTkLabel(
                empty_frame,
                text="Create your first cashbook to start tracking expenses.\nYou can organize them by category or purpose.",
                font=theme.create_font('base'),
                text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary']),
                justify="center"
            )
            empty_subtitle.pack(pady=(0, theme.SPACING['xl']))
        
        # Add enhanced helpful tips
        tips_frame = ctk.CTkFrame(
            empty_frame, 
            fg_color=(theme.DARK_THEME['secondary'], theme.DARK_THEME['secondary']), 
            corner_radius=theme.RADIUS['base']
        )
        tips_frame.pack(fill="x", pady=(0, theme.SPACING['lg']))
        
        tips_title = ctk.CTkLabel(
            tips_frame,
            text="💡 Getting Started Tips",
            font=theme.create_font('sm', 'bold'),
            text_color=(theme.DARK_THEME['text_primary'], theme.DARK_THEME['text_primary']),
            anchor="w"
        )
        tips_title.pack(anchor="w", padx=theme.SPACING['md'], pady=(theme.SPACING['md'], theme.SPACING['sm']))
        
        tips_text = ctk.CTkLabel(
            tips_frame,
            text="• Create separate cashbooks for different purposes\n• Use categories like 'Personal', 'Business', 'Travel'\n• Your data is automatically saved and backed up",
            font=theme.create_font('xs'),
            text_color=(theme.DARK_THEME['text_secondary'], theme.DARK_THEME['text_secondary']),
            anchor="w",
            justify="left"
        )
        tips_text.pack(anchor="w", padx=theme.SPACING['md'], pady=(0, theme.SPACING['md']))
    
    def display_cashbooks_grid(self, cashbooks):
        """
        Display cashbooks in a responsive grid layout.
        
        Args:
            cashbooks: List of Cashbook objects to display
        """
        # Calculate how many cashbooks to show based on layout
        # Always reserve one slot for the create card
        max_visible_cashbooks = self.calculate_max_visible_cashbooks()
        
        # Always add the create new cashbook card first
        create_card = CreateCashbookCard(
            self.grid_frame,
            on_create_callback=self.handle_cashbook_creation
        )
        create_card.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=(10, 5))
        
        # Add existing cashbook cards
        visible_cashbooks = cashbooks[:max_visible_cashbooks - 1]  # -1 for create card
        
        for i, cashbook in enumerate(visible_cashbooks):
            # Calculate position (create card takes 0,0)
            position = i + 1  # Offset by 1 for create card
            row = position // self.cards_per_row
            col = position % self.cards_per_row
            
            # Create cashbook card with responsive padding
            card = CashbookCard(
                self.grid_frame,
                cashbook_data=cashbook,
                on_click_callback=self.handle_cashbook_click,
                on_context_menu_callback=self.handle_cashbook_context_menu
            )
            
            # Calculate padding based on position
            padx = (5, 10) if col == self.cards_per_row - 1 else (5, 5)
            pady = (5, 10) if row > 0 else (10, 5)
            
            card.grid(row=row, column=col, sticky="nsew", padx=padx, pady=pady)
        
        # Add "See all" functionality if there are more cashbooks
        total_cashbooks = self.cashbook_manager.get_metadata().total_cashbooks
        if total_cashbooks > max_visible_cashbooks - 1:  # -1 for create card
            self.add_see_all_link(total_cashbooks)
    
    def calculate_max_visible_cashbooks(self):
        """
        Calculate maximum number of cashbooks to show based on current layout.
        
        Returns:
            int: Maximum number of cashbook cards (including create card)
        """
        if self.current_layout_mode == "mobile":
            return 3  # 1 create + 2 cashbooks in mobile
        elif self.current_layout_mode == "tablet":
            if self.cards_per_row == 1:
                return 4  # 1 create + 3 cashbooks in single column
            else:
                return 4  # 1 create + 3 cashbooks in 2x2 grid
        else:  # desktop
            if self.cards_per_row == 2:
                return 4  # 1 create + 3 cashbooks in 2x2 grid
            else:  # 3 columns
                return 6  # 1 create + 5 cashbooks in 2x3 grid
    
    def handle_cashbook_click(self, cashbook_id: str):
        """
        Handle clicking on a cashbook card to open detail view.
        
        Args:
            cashbook_id: ID of the clicked cashbook
        """
        # Placeholder implementation - will be enhanced in future tasks
        cashbook = self.cashbook_manager.get_cashbook(cashbook_id)
        if cashbook:
            print(f"Opening cashbook: {cashbook.name} (ID: {cashbook_id})")
            self.update_status(f"📖 Opened cashbook '{cashbook.name}' - detail view coming soon!")
        else:
            print(f"Cashbook not found: {cashbook_id}")
            self.update_status("❌ Error: Cashbook not found")
    
    def handle_cashbook_context_menu(self, cashbook_id: str, x: int, y: int):
        """
        Handle right-click context menu on cashbook cards.
        
        Args:
            cashbook_id: ID of the cashbook
            x: Screen x coordinate for menu
            y: Screen y coordinate for menu
        """
        cashbook = self.cashbook_manager.get_cashbook(cashbook_id)
        if not cashbook:
            self.update_status("❌ Error: Cashbook not found")
            return
        
        # Create context menu using CTkMessagebox
        try:
            from CTkMessagebox import CTkMessagebox
            
            # Show context menu with rename and delete options
            msg = CTkMessagebox(
                title=f"Manage '{cashbook.name}'",
                message="Choose an action:",
                icon="question",
                option_1="Cancel",
                option_2="Rename",
                option_3="Delete"
            )
            
            response = msg.get()
            
            if response == "Rename":
                self.handle_cashbook_rename(cashbook_id)
            elif response == "Delete":
                self.handle_cashbook_delete(cashbook_id)
            # Cancel or close does nothing
                
        except ImportError:
            # Fallback to simple print if CTkMessagebox not available
            print(f"Context menu for cashbook: {cashbook.name} at ({x}, {y})")
            self.update_status(f"⚠️ Context menu for '{cashbook.name}' - CTkMessagebox not available")
    
    def add_see_all_link(self, total_count):
        """
        Add a "See all" link when there are more cashbooks than can be displayed.
        
        Args:
            total_count: Total number of cashbooks
        """
        # Remove existing see all button if it exists
        if self.see_all_button:
            self.see_all_button.destroy()
        
        # Create see all frame
        see_all_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        see_all_frame.grid(row=1, column=0, columnspan=self.cards_per_row, pady=20)
        
        # Create see all button with dynamic text
        max_visible = self.calculate_max_visible_cashbooks() - 1  # -1 for create card
        remaining_count = total_count - max_visible
        
        self.see_all_button = ctk.CTkButton(
            see_all_frame,
            text=f"See all {total_count} cashbooks (+{remaining_count} more)",
            command=self.show_all_cashbooks,
            fg_color="transparent",
            text_color=("blue", "lightblue"),
            hover_color=("gray90", "gray20"),
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.see_all_button.pack()
        
        # Store reference to frame for cleanup
        self.see_all_frame = see_all_frame
    
    def _on_frame_configure(self, event=None):
        """Handle frame configuration changes for responsive design."""
        # Only handle if this is the main frame being configured
        if event and event.widget == self:
            # Small delay to avoid excessive recalculations
            self.after_idle(self.configure_grid_layout)
    
    def position_see_all_button(self):
        """Reposition the see all button based on current layout."""
        if hasattr(self, 'see_all_frame') and self.see_all_frame.winfo_exists():
            self.see_all_frame.grid_configure(columnspan=self.cards_per_row)
    
    def show_all_cashbooks(self):
        """Handle showing all cashbooks in an expanded view."""
        # Create a new window or dialog to show all cashbooks
        self.create_all_cashbooks_window()
    
    def create_all_cashbooks_window(self):
        """Create a window to display all cashbooks in a scrollable grid."""
        # Create new window
        all_cashbooks_window = ctk.CTkToplevel(self)
        all_cashbooks_window.title("All Cashbooks")
        all_cashbooks_window.geometry("900x700")
        all_cashbooks_window.minsize(600, 400)
        
        # Configure window grid
        all_cashbooks_window.grid_columnconfigure(0, weight=1)
        all_cashbooks_window.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(all_cashbooks_window, height=60, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="All Cashbooks",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        # Close button
        close_button = ctk.CTkButton(
            header_frame,
            text="Close",
            command=all_cashbooks_window.destroy,
            width=80,
            height=30
        )
        close_button.grid(row=0, column=1, sticky="e", padx=20, pady=15)
        
        # Scrollable content area
        scrollable_frame = ctk.CTkScrollableFrame(all_cashbooks_window)
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Configure grid for all cashbooks
        self.populate_all_cashbooks_grid(scrollable_frame, all_cashbooks_window)
        
        # Center the window
        all_cashbooks_window.transient(self.winfo_toplevel())
        all_cashbooks_window.grab_set()
        
        # Focus on the new window
        all_cashbooks_window.focus()
    
    def populate_all_cashbooks_grid(self, parent_frame, window):
        """
        Populate the all cashbooks window with a grid of all cashbooks.
        
        Args:
            parent_frame: Parent frame to contain the grid
            window: Reference to the window for sizing calculations
        """
        # Get all cashbooks
        all_cashbooks = self.cashbook_manager.get_all_cashbooks()
        
        # Calculate grid layout for the window
        window_width = 900  # Default window width
        cards_per_row = max(2, min(4, window_width // 250))  # 2-4 cards per row
        
        # Configure grid columns
        for i in range(cards_per_row):
            parent_frame.grid_columnconfigure(i, weight=1, minsize=200)
        
        # Add create new cashbook card first
        create_card = CreateCashbookCard(
            parent_frame,
            on_create_callback=lambda name, desc, cat: self.handle_all_cashbooks_creation(
                name, desc, cat, window
            )
        )
        create_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add all existing cashbook cards
        for i, cashbook in enumerate(all_cashbooks):
            position = i + 1  # Offset by 1 for create card
            row = position // cards_per_row
            col = position % cards_per_row
            
            card = CashbookCard(
                parent_frame,
                cashbook_data=cashbook,
                on_click_callback=lambda cb_id: self.handle_all_cashbooks_click(cb_id, window),
                on_context_menu_callback=lambda cb_id, x, y: self.handle_all_cashbooks_context_menu(
                    cb_id, x, y, window
                )
            )
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        
        # Add summary info
        summary_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        summary_frame.grid(
            row=(len(all_cashbooks) // cards_per_row) + 2, 
            column=0, 
            columnspan=cards_per_row, 
            pady=20
        )
        
        total_entries = sum(cb.entry_count for cb in all_cashbooks)
        total_amount = sum(cb.total_amount for cb in all_cashbooks)
        
        summary_label = ctk.CTkLabel(
            summary_frame,
            text=f"Total: {len(all_cashbooks)} cashbooks • {total_entries} entries • ${total_amount:.2f}",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        summary_label.pack()
    
    def handle_all_cashbooks_creation(self, name: str, description: str, category: str, window):
        """Handle cashbook creation from the all cashbooks window."""
        self.handle_cashbook_creation(name, description, category)
        # Refresh the all cashbooks window
        window.destroy()
        self.show_all_cashbooks()
    
    def handle_all_cashbooks_click(self, cashbook_id: str, window):
        """Handle cashbook click from the all cashbooks window."""
        self.handle_cashbook_click(cashbook_id)
        window.destroy()  # Close the all cashbooks window
    
    def handle_all_cashbooks_context_menu(self, cashbook_id: str, x: int, y: int, window):
        """Handle context menu from the all cashbooks window."""
        # Use the same context menu handler but refresh the all cashbooks window after actions
        original_refresh = self.refresh_cashbooks
        
        def refresh_wrapper():
            original_refresh()
            # Refresh the all cashbooks window content
            for widget in window.winfo_children():
                if isinstance(widget, ctk.CTkScrollableFrame):
                    for child in widget.winfo_children():
                        child.destroy()
                    self.populate_all_cashbooks_grid(widget, window)
                    break
        
        # Temporarily replace refresh method
        self.refresh_cashbooks = refresh_wrapper
        
        try:
            self.handle_cashbook_context_menu(cashbook_id, x, y)
        finally:
            # Restore original refresh method
            self.refresh_cashbooks = original_refresh
    
    def show_recovery_info(self):
        """Show data recovery information dialog."""
        recovery_info = self.cashbook_manager.get_error_recovery_info()
        
        # Create recovery info window
        recovery_window = ctk.CTkToplevel(self)
        recovery_window.title("Data Recovery Information")
        recovery_window.geometry("600x500")
        recovery_window.minsize(500, 400)
        
        # Configure window grid
        recovery_window.grid_columnconfigure(0, weight=1)
        recovery_window.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(recovery_window, height=60, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔧 Data Recovery Information",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        # Close button
        close_button = ctk.CTkButton(
            header_frame,
            text="Close",
            command=recovery_window.destroy,
            width=80,
            height=30
        )
        close_button.grid(row=0, column=1, sticky="e", padx=20, pady=15)
        
        # Scrollable content area
        scrollable_frame = ctk.CTkScrollableFrame(recovery_window)
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Recovery status
        status_frame = ctk.CTkFrame(scrollable_frame)
        status_frame.pack(fill="x", pady=(0, 15))
        
        status_title = ctk.CTkLabel(
            status_frame,
            text="Recovery Status",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        status_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        status_text = f"""Data Directory: {recovery_info['data_directory']}
Total Cashbooks: {recovery_info['total_cashbooks']}
Has Backup Files: {'Yes' if recovery_info['has_backups'] else 'No'}
Last Backup: {recovery_info['last_backup'] or 'Never'}"""
        
        status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=ctk.CTkFont(size=11),
            anchor="w",
            justify="left"
        )
        status_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Available backups
        if recovery_info.get("available_backups"):
            backups_frame = ctk.CTkFrame(scrollable_frame)
            backups_frame.pack(fill="x", pady=(0, 15))
            
            backups_title = ctk.CTkLabel(
                backups_frame,
                text="Available Backup Files",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            backups_title.pack(anchor="w", padx=15, pady=(10, 5))
            
            for backup in recovery_info["available_backups"][:5]:  # Show last 5 backups
                backup_text = f"• {backup['filename']} - Created: {backup['created'][:19]} - Size: {backup['size']} bytes"
                backup_label = ctk.CTkLabel(
                    backups_frame,
                    text=backup_text,
                    font=ctk.CTkFont(size=10),
                    anchor="w",
                    text_color=("gray60", "gray40")
                )
                backup_label.pack(anchor="w", padx=25, pady=1)
            
            if len(recovery_info["available_backups"]) > 5:
                more_label = ctk.CTkLabel(
                    backups_frame,
                    text=f"... and {len(recovery_info['available_backups']) - 5} more backup files",
                    font=ctk.CTkFont(size=10),
                    anchor="w",
                    text_color=("gray60", "gray40")
                )
                more_label.pack(anchor="w", padx=25, pady=(5, 10))
            else:
                # Add padding
                ctk.CTkLabel(backups_frame, text="").pack(pady=5)
        
        # Data integrity check
        integrity_frame = ctk.CTkFrame(scrollable_frame)
        integrity_frame.pack(fill="x", pady=(0, 15))
        
        integrity_title = ctk.CTkLabel(
            integrity_frame,
            text="Data Integrity Check",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        integrity_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Run integrity check
        integrity_report = self.cashbook_manager.validate_data_integrity()
        
        if integrity_report["is_valid"]:
            integrity_text = "✅ All data is valid and consistent"
            integrity_color = ("green", "lightgreen")
        else:
            integrity_text = f"⚠️ Found {len(integrity_report['issues'])} data issues"
            integrity_color = ("orange", "yellow")
        
        integrity_status = ctk.CTkLabel(
            integrity_frame,
            text=integrity_text,
            font=ctk.CTkFont(size=12),
            anchor="w",
            text_color=integrity_color
        )
        integrity_status.pack(anchor="w", padx=15, pady=(0, 5))
        
        if not integrity_report["is_valid"]:
            for issue in integrity_report["issues"]:
                issue_label = ctk.CTkLabel(
                    integrity_frame,
                    text=f"• {issue}",
                    font=ctk.CTkFont(size=10),
                    anchor="w",
                    text_color=("gray60", "gray40")
                )
                issue_label.pack(anchor="w", padx=25, pady=1)
        
        ctk.CTkLabel(integrity_frame, text="").pack(pady=5)  # Padding
        
        # Actions
        actions_frame = ctk.CTkFrame(scrollable_frame)
        actions_frame.pack(fill="x", pady=(0, 15))
        
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Available Actions",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        actions_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Create backup button
        backup_button = ctk.CTkButton(
            actions_frame,
            text="Create Backup Now",
            command=lambda: self.create_manual_backup(recovery_window),
            height=35,
            width=150
        )
        backup_button.pack(anchor="w", padx=15, pady=5)
        
        ctk.CTkLabel(actions_frame, text="").pack(pady=5)  # Padding
        
        # Center the window
        recovery_window.transient(self.winfo_toplevel())
        recovery_window.grab_set()
        recovery_window.focus()
    
    def create_manual_backup(self, parent_window):
        """Create a manual backup and show result."""
        try:
            backup_path = self.cashbook_manager.backup_data()
            
            # Show success message
            try:
                from CTkMessagebox import CTkMessagebox
                CTkMessagebox(
                    title="Backup Created",
                    message=f"Backup successfully created at:\n{backup_path}",
                    icon="check",
                    option_1="OK"
                )
            except ImportError:
                self.update_status(f"Backup created: {backup_path}")
            
            # Close recovery window and refresh
            parent_window.destroy()
            
        except Exception as e:
            # Show error message
            try:
                from CTkMessagebox import CTkMessagebox
                CTkMessagebox(
                    title="Backup Failed",
                    message=f"Failed to create backup:\n{str(e)}",
                    icon="cancel",
                    option_1="OK"
                )
            except ImportError:
                self.update_status(f"Backup failed: {str(e)}")
    
    def configure_grid_layout(self):
        """Configure the grid layout based on current window size."""
        # Get current window width
        try:
            window_width = self.winfo_width()
            if window_width <= 1:  # Window not yet rendered
                window_width = 800  # Default width
        except:
            window_width = 800
        
        # Determine layout mode and cards per row
        if window_width < 500:
            # Mobile layout: 1 column
            layout_mode = "mobile"
            cards_per_row = 1
            min_card_width = 280
        elif window_width < 800:
            # Tablet layout: 1-2 columns depending on content
            layout_mode = "tablet"
            cards_per_row = 1 if window_width < 600 else 2
            min_card_width = 250
        else:
            # Desktop layout: 2-3 columns
            layout_mode = "desktop"
            cards_per_row = 2 if window_width < 1000 else 3
            min_card_width = 200
        
        # Update layout if changed
        if (not hasattr(self, 'current_layout_mode') or 
            self.current_layout_mode != layout_mode or
            self.cards_per_row != cards_per_row):
            
            self.current_layout_mode = layout_mode
            self.cards_per_row = cards_per_row
            
            # Configure grid columns
            for i in range(4):  # Clear all columns first
                self.grid_frame.grid_columnconfigure(i, weight=0, minsize=0)
            
            # Configure active columns with proper spacing
            for i in range(cards_per_row):
                self.grid_frame.grid_columnconfigure(i, weight=1, minsize=min_card_width, pad=5)
            
            # Configure row spacing
            for i in range(3):  # Up to 3 rows for most layouts
                self.grid_frame.grid_rowconfigure(i, pad=5)
            
            # Refresh layout if we have cashbooks
            if hasattr(self, 'cashbook_manager'):
                self.refresh_cashbooks()

    def handle_resize(self, event=None):
        """
        Handle window resize events for responsive design.
        
        Args:
            event: Tkinter event object (optional)
        """
        # Reconfigure grid layout based on new window size
        self.configure_grid_layout()
        
        # Update see all button position if it exists
        if self.see_all_button:
            self.position_see_all_button()
    
    def handle_cashbook_creation(self, name: str, description: str, category: str):
        """
        Handle the creation of a new cashbook with comprehensive error handling.
        
        Args:
            name: Name of the new cashbook
            description: Optional description
            category: Optional category
        """
        try:
            # Create the cashbook using the manager
            cashbook = self.cashbook_manager.create_cashbook(
                name=name,
                description=description,
                category=category
            )
            
            # Refresh the dashboard to show the new cashbook
            self.refresh_cashbooks()
            
            # Update status
            self.update_status(f"Created cashbook '{name}' successfully")
            
        except ValueError as e:
            # Handle validation errors
            self.show_error_dialog(
                "Invalid Input",
                f"Cannot create cashbook: {str(e)}",
                "Please check your input and try again."
            )
        except (FileOperationError, IOError, OSError) as e:
            # Handle file operation errors
            self.show_error_dialog(
                "File Operation Error",
                f"Cannot save cashbook data: {str(e)}",
                "Please check file permissions and available disk space."
            )
        except Exception as e:
            # Handle unexpected errors
            self.show_error_dialog(
                "Unexpected Error",
                f"Failed to create cashbook: {str(e)}",
                "Please try again or contact support if the problem persists."
            )
    
    def show_error_dialog(self, title: str, message: str, suggestion: str = ""):
        """
        Show a user-friendly error dialog with recovery suggestions.
        
        Args:
            title: Error dialog title
            message: Main error message
            suggestion: Optional suggestion for recovery
        """
        try:
            from CTkMessagebox import CTkMessagebox
            
            full_message = message
            if suggestion:
                full_message += f"\n\n{suggestion}"
            
            CTkMessagebox(
                title=title,
                message=full_message,
                icon="cancel",
                option_1="OK"
            )
        except ImportError:
            # Fallback to tkinter messagebox
            try:
                from tkinter import messagebox
                full_message = message
                if suggestion:
                    full_message += f"\n\n{suggestion}"
                messagebox.showerror(title, full_message)
            except ImportError:
                # Last resort: update status
                self.update_status(f"Error: {message}")
    
    def show_warning_dialog(self, title: str, message: str, suggestion: str = ""):
        """
        Show a user-friendly warning dialog.
        
        Args:
            title: Warning dialog title
            message: Main warning message
            suggestion: Optional suggestion
        """
        try:
            from CTkMessagebox import CTkMessagebox
            
            full_message = message
            if suggestion:
                full_message += f"\n\n{suggestion}"
            
            CTkMessagebox(
                title=title,
                message=full_message,
                icon="warning",
                option_1="OK"
            )
        except ImportError:
            # Fallback to tkinter messagebox
            try:
                from tkinter import messagebox
                full_message = message
                if suggestion:
                    full_message += f"\n\n{suggestion}"
                messagebox.showwarning(title, full_message)
            except ImportError:
                # Last resort: update status
                self.update_status(f"Warning: {message}")
    
    def handle_cashbook_rename(self, cashbook_id: str):
        """
        Handle renaming a cashbook with inline input dialog.
        
        Args:
            cashbook_id: ID of the cashbook to rename
        """
        cashbook = self.cashbook_manager.get_cashbook(cashbook_id)
        if not cashbook:
            self.update_status("Error: Cashbook not found")
            return
        
        try:
            from CTkMessagebox import CTkMessagebox
            import customtkinter as ctk
            
            # Create a custom input dialog for renaming
            dialog = ctk.CTkInputDialog(
                text=f"Enter new name for '{cashbook.name}':",
                title="Rename Cashbook"
            )
            
            new_name = dialog.get_input()
            
            if new_name and new_name.strip():
                new_name = new_name.strip()
                
                # Validate the new name
                if len(new_name) < 1:
                    CTkMessagebox(
                        title="Invalid Name",
                        message="Cashbook name cannot be empty.",
                        icon="cancel",
                        option_1="OK"
                    )
                    return
                
                if len(new_name) > 50:
                    CTkMessagebox(
                        title="Invalid Name",
                        message="Cashbook name cannot exceed 50 characters.",
                        icon="cancel",
                        option_1="OK"
                    )
                    return
                
                # Check if name already exists
                existing_cashbooks = self.cashbook_manager.get_all_cashbooks()
                if any(cb.name.lower() == new_name.lower() and cb.id != cashbook_id 
                       for cb in existing_cashbooks):
                    CTkMessagebox(
                        title="Name Already Exists",
                        message=f"A cashbook named '{new_name}' already exists.",
                        icon="cancel",
                        option_1="OK"
                    )
                    return
                
                # Update the cashbook name
                try:
                    self.cashbook_manager.update_cashbook(cashbook_id, name=new_name)
                    self.refresh_cashbooks()
                    self.update_status(f"Renamed cashbook to '{new_name}'")
                    
                    # Show success message
                    CTkMessagebox(
                        title="Success",
                        message=f"Cashbook renamed to '{new_name}' successfully!",
                        icon="check",
                        option_1="OK"
                    )
                    
                except ValueError as e:
                    CTkMessagebox(
                        title="Invalid Input",
                        message=f"Cannot rename cashbook: {str(e)}",
                        icon="cancel",
                        option_1="OK"
                    )
                except (FileOperationError, IOError, OSError) as e:
                    CTkMessagebox(
                        title="File Operation Error",
                        message=f"Cannot save changes: {str(e)}\n\nPlease check file permissions and try again.",
                        icon="cancel",
                        option_1="OK"
                    )
                except Exception as e:
                    CTkMessagebox(
                        title="Unexpected Error",
                        message=f"Failed to rename cashbook: {str(e)}\n\nPlease try again or restart the application.",
                        icon="cancel",
                        option_1="OK"
                    )
            
        except ImportError:
            # Fallback if CTkMessagebox not available
            self.update_status("Rename feature requires CTkMessagebox")
    
    def handle_cashbook_delete(self, cashbook_id: str):
        """
        Handle deleting a cashbook with confirmation dialog.
        
        Args:
            cashbook_id: ID of the cashbook to delete
        """
        cashbook = self.cashbook_manager.get_cashbook(cashbook_id)
        if not cashbook:
            self.update_status("Error: Cashbook not found")
            return
        
        try:
            from CTkMessagebox import CTkMessagebox
            
            # Show confirmation dialog
            msg = CTkMessagebox(
                title="Delete Cashbook",
                message=f"Are you sure you want to delete '{cashbook.name}'?\n\n"
                       f"This action cannot be undone and will permanently remove:\n"
                       f"• {cashbook.entry_count} entries\n"
                       f"• All transaction data\n"
                       f"• Associated metadata",
                icon="warning",
                option_1="Cancel",
                option_2="Delete"
            )
            
            response = msg.get()
            
            if response == "Delete":
                try:
                    # Delete the cashbook
                    success = self.cashbook_manager.delete_cashbook(cashbook_id)
                    if success:
                        self.refresh_cashbooks()
                        self.update_status(f"Deleted cashbook '{cashbook.name}' successfully")
                        
                        # Show success message
                        CTkMessagebox(
                            title="Deleted",
                            message=f"Cashbook '{cashbook.name}' has been deleted successfully.",
                            icon="check",
                            option_1="OK"
                        )
                    else:
                        CTkMessagebox(
                            title="Error",
                            message=f"Cashbook '{cashbook.name}' could not be found for deletion.",
                            icon="cancel",
                            option_1="OK"
                        )
                        
                except (FileOperationError, IOError, OSError) as e:
                    CTkMessagebox(
                        title="File Operation Error",
                        message=f"Cannot delete cashbook: {str(e)}\n\nPlease check file permissions and try again.",
                        icon="cancel",
                        option_1="OK"
                    )
                except Exception as e:
                    CTkMessagebox(
                        title="Unexpected Error",
                        message=f"Failed to delete cashbook: {str(e)}\n\nPlease try again or restart the application.",
                        icon="cancel",
                        option_1="OK"
                    )
                    
                    # Show success message
                    CTkMessagebox(
                        title="Deleted",
                        message=f"Cashbook '{cashbook.name}' has been deleted successfully.",
                        icon="check",
                        option_1="OK"
                    )
                    
                except Exception as e:
                    CTkMessagebox(
                        title="Error",
                        message=f"Failed to delete cashbook: {str(e)}",
                        icon="cancel",
                        option_1="OK"
                    )
            
        except ImportError:
            # Fallback if CTkMessagebox not available
            self.update_status("Delete feature requires CTkMessagebox")
    
    def update_status(self, message: str):
        """
        Update the status message in the footer with enhanced styling.
        
        Args:
            message: Status message to display
        """
        # Determine status type and color based on message content
        if "error" in message.lower() or "❌" in message:
            text_color = (theme.DARK_THEME['error'], theme.DARK_THEME['error'])
        elif "success" in message.lower() or "✅" in message:
            text_color = (theme.DARK_THEME['success'], theme.DARK_THEME['success'])
        elif "warning" in message.lower() or "⚠️" in message:
            text_color = (theme.DARK_THEME['warning'], theme.DARK_THEME['warning'])
        else:
            text_color = (theme.DARK_THEME['text_muted'], theme.DARK_THEME['text_muted'])
        
        self.status_label.configure(
            text=message,
            text_color=text_color
        )
        
        # Auto-clear status after 3 seconds
        self.after(3000, lambda: self.status_label.configure(
            text="✅ Ready",
            text_color=(theme.DARK_THEME['text_muted'], theme.DARK_THEME['text_muted'])
        ))
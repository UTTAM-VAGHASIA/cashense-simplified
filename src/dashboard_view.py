"""
Dashboard View for the Cashbook Dashboard application.

This module contains the DashboardView class that provides the main
dashboard interface for managing cashbooks, replacing the simple
welcome screen with a modern card-based layout.
"""

import customtkinter as ctk
from typing import Optional, Callable
try:
    from cashbook_manager import CashbookManager
    from create_cashbook_card import CreateCashbookCard
    from cashbook_card import CashbookCard
except ImportError:
    from .cashbook_manager import CashbookManager
    from .create_cashbook_card import CreateCashbookCard
    from .cashbook_card import CashbookCard


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
        """Create the header section with title and navigation."""
        header_frame = ctk.CTkFrame(self, height=80, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_propagate(False)  # Maintain fixed height
        
        # Main title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Recent cashbooks",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=30, pady=25)
        
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
        """Create the footer section for status and additional actions."""
        footer_frame = ctk.CTkFrame(self, height=40, corner_radius=0)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_propagate(False)  # Maintain fixed height
        
        # Status label (placeholder for now)
        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        self.footer_frame = footer_frame
    
    def refresh_cashbooks(self):
        """Refresh the display of cashbooks in the grid."""
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
        recent_cashbooks = self.cashbook_manager.get_recent_cashbooks(limit=max_visible)
        
        if not recent_cashbooks:
            # Show empty state
            self.show_empty_state()
        else:
            # Display cashbooks in grid
            self.display_cashbooks_grid(recent_cashbooks)
    
    def show_empty_state(self):
        """Display empty state when no cashbooks exist."""
        # Add the create new cashbook card
        create_card = CreateCashbookCard(
            self.grid_frame,
            on_create_callback=self.handle_cashbook_creation
        )
        create_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add empty state message in the remaining space
        empty_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        empty_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=20, pady=40)
        
        # Empty state icon and message
        empty_icon = ctk.CTkLabel(
            empty_frame,
            text="📚",
            font=ctk.CTkFont(size=48)
        )
        empty_icon.pack(pady=(30, 10))
        
        empty_title = ctk.CTkLabel(
            empty_frame,
            text="No cashbooks yet",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        empty_title.pack(pady=(0, 5))
        
        empty_subtitle = ctk.CTkLabel(
            empty_frame,
            text="Create your first cashbook to start tracking expenses",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray40")
        )
        empty_subtitle.pack(pady=(0, 30))
    
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
            self.update_status(f"Opened cashbook '{cashbook.name}' - detail view coming soon!")
        else:
            print(f"Cashbook not found: {cashbook_id}")
            self.update_status("Error: Cashbook not found")
    
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
            self.update_status("Error: Cashbook not found")
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
            self.update_status(f"Context menu for '{cashbook.name}' - CTkMessagebox not available")
    
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
        Handle the creation of a new cashbook.
        
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
            
        except Exception as e:
            # Show error message
            from tkinter import messagebox
            messagebox.showerror(
                "Error Creating Cashbook",
                f"Failed to create cashbook: {str(e)}"
            )
    
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
                    
                except Exception as e:
                    CTkMessagebox(
                        title="Error",
                        message=f"Failed to rename cashbook: {str(e)}",
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
                    self.cashbook_manager.delete_cashbook(cashbook_id)
                    self.refresh_cashbooks()
                    self.update_status(f"Deleted cashbook '{cashbook.name}'")
                    
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
        Update the status message in the footer.
        
        Args:
            message: Status message to display
        """
        self.status_label.configure(text=message)
        
        # Auto-clear status after 3 seconds
        self.after(3000, lambda: self.status_label.configure(text="Ready"))
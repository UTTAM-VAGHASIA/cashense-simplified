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
        
        # Configure grid weights for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Main content area expands
        
        self.setup_layout()
        self.refresh_cashbooks()
    
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
        
        # Configure grid for 2x2 layout (responsive)
        self.grid_frame.grid_columnconfigure(0, weight=1, minsize=200)
        self.grid_frame.grid_columnconfigure(1, weight=1, minsize=200)
        
        # Add some spacing between grid items
        self.grid_frame.grid_rowconfigure(0, pad=10)
        self.grid_frame.grid_rowconfigure(1, pad=10)
    
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
        
        # Get recent cashbooks (up to 4 for the grid)
        recent_cashbooks = self.cashbook_manager.get_recent_cashbooks(limit=4)
        
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
        Display cashbooks in a 2x2 grid layout.
        
        Args:
            cashbooks: List of Cashbook objects to display
        """
        # Always add the create new cashbook card first
        create_card = CreateCashbookCard(
            self.grid_frame,
            on_create_callback=self.handle_cashbook_creation
        )
        create_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add existing cashbook cards (up to 3 more to make 4 total with create card)
        for i, cashbook in enumerate(cashbooks[:3]):  # Limit to 3 for 2x2 grid with create card
            # Calculate position (create card takes 0,0)
            if i == 0:
                row, col = 0, 1
            elif i == 1:
                row, col = 1, 0
            else:  # i == 2
                row, col = 1, 1
            
            # Create cashbook card
            card = CashbookCard(
                self.grid_frame,
                cashbook_data=cashbook,
                on_click_callback=self.handle_cashbook_click,
                on_context_menu_callback=self.handle_cashbook_context_menu
            )
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        
        # Add "See all" link if there are more than 3 cashbooks (since create card takes one slot)
        total_cashbooks = self.cashbook_manager.get_metadata().total_cashbooks
        if total_cashbooks > 3:
            self.add_see_all_link(total_cashbooks)
    
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
        Add a "See all" link when there are more than 4 cashbooks.
        
        Args:
            total_count: Total number of cashbooks
        """
        see_all_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        see_all_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        see_all_button = ctk.CTkButton(
            see_all_frame,
            text=f"See all {total_count} cashbooks",
            command=self.show_all_cashbooks,
            fg_color="transparent",
            text_color=("blue", "lightblue"),
            hover_color=("gray90", "gray20"),
            font=ctk.CTkFont(size=14)
        )
        see_all_button.pack()
    
    def show_all_cashbooks(self):
        """Handle showing all cashbooks (placeholder for future implementation)."""
        # This will be implemented in a future task
        print("Show all cashbooks - feature coming soon!")
    
    def handle_resize(self, event=None):
        """
        Handle window resize events for responsive design.
        
        Args:
            event: Tkinter event object (optional)
        """
        # Get current window width
        window_width = self.winfo_width()
        
        if window_width < 600:
            # Switch to single column layout for narrow windows
            self.grid_frame.grid_columnconfigure(1, weight=0, minsize=0)
        else:
            # Use two column layout for wider windows
            self.grid_frame.grid_columnconfigure(1, weight=1, minsize=200)
    
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
import customtkinter as ctk
from tkinter import messagebox
import sys
try:
    from dashboard_view import DashboardView
    from cashbook_manager import CashbookManager
    from theme_manager import theme, animations, icons
except ImportError:
    from .dashboard_view import DashboardView
    from .cashbook_manager import CashbookManager
    from .theme_manager import theme, animations, icons

class CashenseApp:
    def __init__(self):
        # Set appearance mode and enhanced color theme
        ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        # Create main window with enhanced styling
        self.root = ctk.CTk()
        self.root.title("💰 Cashense - Personal Finance Tracker")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Apply enhanced window styling
        self.root.configure(fg_color=theme.DARK_THEME['background'])
        
        # Initialize cashbook manager
        self.cashbook_manager = CashbookManager()
        
        # Set up window close protocol for proper cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Configure main window grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create and display dashboard view
        self.dashboard_view = DashboardView(
            self.root, 
            self.cashbook_manager,
            corner_radius=0
        )
        self.dashboard_view.grid(row=0, column=0, sticky="nsew")
        
        # Bind resize event for responsive design
        self.root.bind("<Configure>", self.on_window_resize)
    
    def on_window_resize(self, event=None):
        """Handle window resize events for responsive design."""
        # Only handle resize events for the main window
        if event and event.widget == self.root:
            self.dashboard_view.handle_resize(event)
    
    def update_status(self, message):
        """Update status message in the dashboard."""
        if hasattr(self, 'dashboard_view'):
            self.dashboard_view.update_status(message)
    
    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()
    
    def on_closing(self):
        """Handle application closing with proper cleanup and data saving."""
        try:
            # Ensure all data is saved before closing
            # The CashbookManager automatically saves data on operations,
            # but we can trigger a final save to be safe
            if hasattr(self, 'cashbook_manager'):
                # Force a final metadata update and save
                self.cashbook_manager._update_metadata()
                self.cashbook_manager._save_data()
            
            # Update status to indicate saving
            if hasattr(self, 'dashboard_view'):
                self.dashboard_view.update_status("Saving data...")
                # Give a brief moment for the status to show
                self.root.after(100, self._finalize_close)
            else:
                self._finalize_close()
                
        except Exception as e:
            print(f"Error during application close: {e}")
            # Still close the application even if there's an error
            self._finalize_close()
    
    def _finalize_close(self):
        """Finalize the application close process."""
        self.root.quit()
        self.root.destroy()
    
    def quit_app(self):
        """Legacy quit method - delegates to proper close handler."""
        self.on_closing()

def main():
    app = CashenseApp()
    app.run()

if __name__ == "__main__":
    main()
import customtkinter as ctk
from tkinter import messagebox
import sys
try:
    from dashboard_view import DashboardView
    from cashbook_manager import CashbookManager
except ImportError:
    from .dashboard_view import DashboardView
    from .cashbook_manager import CashbookManager

class CashenseApp:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Cashense - Personal Finance Tracker")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize cashbook manager
        self.cashbook_manager = CashbookManager()
        
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
    
    def quit_app(self):
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

def main():
    app = CashenseApp()
    app.run()

if __name__ == "__main__":
    main()
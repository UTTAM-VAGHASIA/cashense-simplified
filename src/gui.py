import customtkinter as ctk
from tkinter import messagebox
import sys

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
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main title
        title_label = ctk.CTkLabel(
            self.root, 
            text="💰 Cashense", 
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=30)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            self.root, 
            text="Your Intelligent Finance Companion", 
            font=ctk.CTkFont(size=16)
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Main frame for buttons
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            button_frame, 
            text="Welcome to Cashense!\nYour personal finance tracking journey starts here.", 
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        welcome_label.pack(pady=30)
        
        # Action buttons
        self.create_action_buttons(button_frame)
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            self.root, 
            text="Ready", 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="bottom", pady=10)
    
    def create_action_buttons(self, parent):
        # Button container
        button_container = ctk.CTkFrame(parent)
        button_container.pack(pady=20)
        
        # Add Transaction button
        add_transaction_btn = ctk.CTkButton(
            button_container,
            text="📝 Add Transaction",
            command=self.add_transaction,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_transaction_btn.pack(pady=10)
        
        # View Balance button
        view_balance_btn = ctk.CTkButton(
            button_container,
            text="💳 View Balance",
            command=self.view_balance,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        view_balance_btn.pack(pady=10)
        
        # View History button
        view_history_btn = ctk.CTkButton(
            button_container,
            text="📊 Transaction History",
            command=self.view_history,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        view_history_btn.pack(pady=10)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            button_container,
            text="⚙️ Settings",
            command=self.open_settings,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_btn.pack(pady=10)
    
    def add_transaction(self):
        self.update_status("Opening Add Transaction...")
        messagebox.showinfo("Add Transaction", "Add Transaction feature coming soon!")
    
    def view_balance(self):
        self.update_status("Checking balance...")
        messagebox.showinfo("Balance", "Current Balance: $0.00\n\nBalance tracking feature coming soon!")
    
    def view_history(self):
        self.update_status("Loading transaction history...")
        messagebox.showinfo("Transaction History", "Transaction history feature coming soon!")
    
    def open_settings(self):
        self.update_status("Opening settings...")
        messagebox.showinfo("Settings", "Settings panel coming soon!")
    
    def update_status(self, message):
        self.status_label.configure(text=message)
        self.root.after(2000, lambda: self.status_label.configure(text="Ready"))
    
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
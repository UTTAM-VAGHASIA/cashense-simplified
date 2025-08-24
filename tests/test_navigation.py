"""
Tests for navigation functionality between dashboard and detail views.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import customtkinter as ctk
    from gui import CashenseApp
    from cashbook_manager import CashbookManager
    from models import Cashbook
    from datetime import datetime
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False


@unittest.skipUnless(CUSTOMTKINTER_AVAILABLE, "CustomTkinter not available")
class TestNavigation(unittest.TestCase):
    """Test navigation between dashboard and detail views."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the mainloop to prevent GUI from actually running
        with patch.object(ctk.CTk, 'mainloop'):
            self.app = CashenseApp()
        
        # Create a test cashbook
        self.test_cashbook = Cashbook(
            id="test-cashbook-id",
            name="Test Cashbook",
            description="Test description",
            category="Test",
            created_date=datetime.now(),
            last_modified=datetime.now(),
            entry_count=5,
            total_amount=150.75,
            icon_color="#FF5722"
        )
        
        # Add test cashbook to manager
        self.app.cashbook_manager._cashbooks[self.test_cashbook.id] = self.test_cashbook
    
    def test_initial_view_is_dashboard(self):
        """Test that the initial view is the dashboard."""
        self.assertEqual(self.app.current_view, "dashboard")
        self.assertIsNotNone(self.app.dashboard_view)
        self.assertIsNone(self.app.detail_view)
    
    def test_navigate_to_cashbook_detail(self):
        """Test navigation to cashbook detail view."""
        # Navigate to detail view
        self.app.navigate_to_cashbook_detail(self.test_cashbook.id)
        
        # Verify navigation state
        self.assertEqual(self.app.current_view, "detail")
        self.assertIsNotNone(self.app.detail_view)
        
        # Verify detail view has correct cashbook data
        self.assertEqual(self.app.detail_view.cashbook_id, self.test_cashbook.id)
        self.assertEqual(self.app.detail_view.cashbook_data.name, "Test Cashbook")
    
    def test_navigate_back_to_dashboard(self):
        """Test navigation back to dashboard from detail view."""
        # First navigate to detail view
        self.app.navigate_to_cashbook_detail(self.test_cashbook.id)
        self.assertEqual(self.app.current_view, "detail")
        
        # Then navigate back to dashboard
        self.app.navigate_back_to_dashboard()
        
        # Verify we're back on dashboard
        self.assertEqual(self.app.current_view, "dashboard")
        self.assertIsNotNone(self.app.dashboard_view)
    
    def test_window_title_updates(self):
        """Test that window title updates during navigation."""
        # Initial title should be default
        initial_title = self.app.root.title()
        self.assertIn("Cashense", initial_title)
        
        # Navigate to detail view
        self.app.navigate_to_cashbook_detail(self.test_cashbook.id)
        detail_title = self.app.root.title()
        self.assertIn("Test Cashbook", detail_title)
        
        # Navigate back to dashboard
        self.app.navigate_back_to_dashboard()
        dashboard_title = self.app.root.title()
        self.assertEqual(dashboard_title, initial_title)
    
    def test_navigate_to_nonexistent_cashbook(self):
        """Test navigation to a cashbook that doesn't exist."""
        # Try to navigate to non-existent cashbook
        self.app.navigate_to_cashbook_detail("nonexistent-id")
        
        # Should still create detail view but show error state
        self.assertEqual(self.app.current_view, "detail")
        self.assertIsNotNone(self.app.detail_view)
        self.assertIsNone(self.app.detail_view.cashbook_data)
    
    def test_dashboard_callback_integration(self):
        """Test that dashboard view uses the navigation callback."""
        # Verify dashboard has the navigation callback
        self.assertIsNotNone(self.app.dashboard_view.on_cashbook_click)
        
        # Test that clicking through dashboard navigates to detail view
        initial_view = self.app.current_view
        self.app.dashboard_view.handle_cashbook_click(self.test_cashbook.id)
        
        # Should have navigated to detail view
        self.assertEqual(self.app.current_view, "detail")
        self.assertNotEqual(self.app.current_view, initial_view)
    
    def test_detail_view_back_callback(self):
        """Test that detail view back button uses the navigation callback."""
        # Navigate to detail view
        self.app.navigate_to_cashbook_detail(self.test_cashbook.id)
        self.assertEqual(self.app.current_view, "detail")
        
        # Test that back navigation works
        self.app.detail_view.handle_back_navigation()
        
        # Should have navigated back to dashboard
        self.assertEqual(self.app.current_view, "dashboard")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'app') and self.app.root:
            self.app.root.destroy()


if __name__ == '__main__':
    unittest.main()
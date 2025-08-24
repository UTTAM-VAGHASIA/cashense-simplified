"""
Tests for the CashbookCard component.

This module contains unit tests for the CashbookCard class to ensure
proper display of cashbook information and event handling.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import customtkinter as ctk
    from models import Cashbook
    from cashbook_card import CashbookCard
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False


@unittest.skipUnless(CUSTOMTKINTER_AVAILABLE, "CustomTkinter not available")
class TestCashbookCard(unittest.TestCase):
    """Test cases for the CashbookCard component."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test root window
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide the window during testing
        
        # Create test cashbook data
        self.test_cashbook = Cashbook(
            id="test-123",
            name="Test Cashbook",
            description="A test cashbook",
            category="Personal",
            created_date=datetime.now() - timedelta(days=5),
            last_modified=datetime.now() - timedelta(days=2),
            entry_count=10,
            total_amount=250.75,
            icon_color="#FF5722"
        )
        
        # Create mock callbacks
        self.mock_click_callback = Mock()
        self.mock_context_callback = Mock()
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_card_initialization(self):
        """Test that the card initializes correctly with cashbook data."""
        card = CashbookCard(
            self.root,
            cashbook_data=self.test_cashbook,
            on_click_callback=self.mock_click_callback
        )
        
        # Check that the card was created
        self.assertIsInstance(card, CashbookCard)
        self.assertEqual(card.cashbook_data, self.test_cashbook)
        self.assertEqual(card.on_click_callback, self.mock_click_callback)
    
    def test_card_with_context_menu(self):
        """Test card initialization with context menu callback."""
        card = CashbookCard(
            self.root,
            cashbook_data=self.test_cashbook,
            on_click_callback=self.mock_click_callback,
            on_context_menu_callback=self.mock_context_callback
        )
        
        self.assertEqual(card.on_context_menu_callback, self.mock_context_callback)
    
    def test_date_formatting(self):
        """Test the date formatting functionality."""
        card = CashbookCard(
            self.root,
            cashbook_data=self.test_cashbook,
            on_click_callback=self.mock_click_callback
        )
        
        # Test today
        today = datetime.now()
        self.assertEqual(card.format_date(today), "Today")
        
        # Test yesterday
        yesterday = datetime.now() - timedelta(days=1)
        self.assertEqual(card.format_date(yesterday), "Yesterday")
        
        # Test days ago
        five_days_ago = datetime.now() - timedelta(days=5)
        self.assertEqual(card.format_date(five_days_ago), "5 days ago")
        
        # Test weeks ago
        two_weeks_ago = datetime.now() - timedelta(days=14)
        self.assertEqual(card.format_date(two_weeks_ago), "2 weeks ago")
    
    def test_click_handling(self):
        """Test that click events are handled correctly."""
        card = CashbookCard(
            self.root,
            cashbook_data=self.test_cashbook,
            on_click_callback=self.mock_click_callback
        )
        
        # Simulate a click
        card.handle_click()
        
        # Verify callback was called with correct cashbook ID
        self.mock_click_callback.assert_called_once_with("test-123")
    
    def test_context_menu_handling(self):
        """Test that context menu events are handled correctly."""
        card = CashbookCard(
            self.root,
            cashbook_data=self.test_cashbook,
            on_click_callback=self.mock_click_callback,
            on_context_menu_callback=self.mock_context_callback
        )
        
        # Create a mock event with coordinates
        mock_event = Mock()
        mock_event.x = 50
        mock_event.y = 30
        
        # Mock the winfo methods to return test coordinates
        card.winfo_rootx = Mock(return_value=100)
        card.winfo_rooty = Mock(return_value=200)
        
        # Simulate a context menu event
        card.handle_context_menu(mock_event)
        
        # Verify callback was called with correct parameters
        self.mock_context_callback.assert_called_once_with("test-123", 150, 230)
    
    def test_update_display(self):
        """Test updating the card display with new data."""
        card = CashbookCard(
            self.root,
            cashbook_data=self.test_cashbook,
            on_click_callback=self.mock_click_callback
        )
        
        # Create new cashbook data
        new_cashbook = Cashbook(
            id="test-456",
            name="Updated Cashbook",
            description="Updated description",
            category="Business",
            entry_count=20,
            total_amount=500.00
        )
        
        # Update the display
        card.update_display(new_cashbook)
        
        # Verify the data was updated
        self.assertEqual(card.cashbook_data, new_cashbook)
    
    def test_long_name_truncation(self):
        """Test that long cashbook names are properly truncated."""
        long_name_cashbook = Cashbook(
            id="test-long",
            name="This is a very long cashbook name that should be truncated",
            entry_count=5,
            total_amount=100.00
        )
        
        card = CashbookCard(
            self.root,
            cashbook_data=long_name_cashbook,
            on_click_callback=self.mock_click_callback
        )
        
        # The card should handle long names gracefully
        self.assertIsInstance(card, CashbookCard)
    
    def test_empty_category_handling(self):
        """Test handling of cashbooks without categories."""
        no_category_cashbook = Cashbook(
            id="test-no-cat",
            name="No Category Cashbook",
            category="",  # Empty category
            entry_count=3,
            total_amount=75.50
        )
        
        card = CashbookCard(
            self.root,
            cashbook_data=no_category_cashbook,
            on_click_callback=self.mock_click_callback
        )
        
        # Should handle empty category gracefully
        self.assertIsInstance(card, CashbookCard)
    
    def test_zero_entries_handling(self):
        """Test handling of cashbooks with zero entries."""
        empty_cashbook = Cashbook(
            id="test-empty",
            name="Empty Cashbook",
            entry_count=0,
            total_amount=0.0
        )
        
        card = CashbookCard(
            self.root,
            cashbook_data=empty_cashbook,
            on_click_callback=self.mock_click_callback
        )
        
        # Should handle zero entries gracefully
        self.assertIsInstance(card, CashbookCard)


if __name__ == '__main__':
    unittest.main()
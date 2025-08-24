"""
Tests for the CreateCashbookCard component.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import customtkinter as ctk
    from create_cashbook_card import CreateCashbookCard, CashbookCreationDialog
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False


@unittest.skipUnless(CUSTOMTKINTER_AVAILABLE, "CustomTkinter not available")
class TestCreateCashbookCard(unittest.TestCase):
    """Test cases for CreateCashbookCard component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = ctk.CTk()
        self.callback_mock = Mock()
        self.card = CreateCashbookCard(self.root, self.callback_mock)
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_card_initialization(self):
        """Test that the card initializes correctly."""
        self.assertIsInstance(self.card, CreateCashbookCard)
        self.assertEqual(self.card.on_create_callback, self.callback_mock)
        
        # Check that UI elements are created
        self.assertTrue(hasattr(self.card, 'plus_icon'))
        self.assertTrue(hasattr(self.card, 'create_label'))
    
    def test_card_styling(self):
        """Test that the card has correct styling."""
        # Check dimensions
        self.assertEqual(self.card.cget('width'), 250)
        self.assertEqual(self.card.cget('height'), 150)
        
        # Check that it has border
        self.assertEqual(self.card.cget('border_width'), 2)
    
    def test_plus_icon_text(self):
        """Test that the plus icon displays correct text."""
        self.assertEqual(self.card.plus_icon.cget('text'), '＋')
    
    def test_create_label_text(self):
        """Test that the create label displays correct text."""
        self.assertEqual(self.card.create_label.cget('text'), 'Create new cashbook')
    
    @patch('create_cashbook_card.CashbookCreationDialog')
    def test_handle_click(self, mock_dialog_class):
        """Test that clicking the card opens the creation dialog."""
        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog
        
        # Simulate click
        self.card.handle_click()
        
        # Verify dialog was created and shown
        mock_dialog_class.assert_called_once()
        mock_dialog.show.assert_called_once()


@unittest.skipUnless(CUSTOMTKINTER_AVAILABLE, "CustomTkinter not available")
class TestCashbookCreationDialog(unittest.TestCase):
    """Test cases for CashbookCreationDialog."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = ctk.CTk()
        self.callback_mock = Mock()
        self.dialog_class = CashbookCreationDialog(self.root, self.callback_mock)
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_dialog_initialization(self):
        """Test that the dialog initializes correctly."""
        self.assertEqual(self.dialog_class.parent, self.root)
        self.assertEqual(self.dialog_class.on_create_callback, self.callback_mock)
        self.assertIsNotNone(self.dialog_class.categories)
        self.assertIn("Personal", self.dialog_class.categories)
        self.assertIn("Business", self.dialog_class.categories)
    
    def test_validate_form_empty_name(self):
        """Test form validation with empty name."""
        # Create dialog UI first
        self.dialog_class.show()
        
        # Test empty name
        self.dialog_class.name_entry.insert(0, "")
        is_valid, error = self.dialog_class.validate_form()
        
        self.assertFalse(is_valid)
        self.assertIn("required", error.lower())
        
        # Clean up
        self.dialog_class.dialog.destroy()
    
    def test_validate_form_short_name(self):
        """Test form validation with too short name."""
        # Create dialog UI first
        self.dialog_class.show()
        
        # Test short name
        self.dialog_class.name_entry.insert(0, "A")
        is_valid, error = self.dialog_class.validate_form()
        
        self.assertFalse(is_valid)
        self.assertIn("2 characters", error)
        
        # Clean up
        self.dialog_class.dialog.destroy()
    
    def test_validate_form_long_name(self):
        """Test form validation with too long name."""
        # Create dialog UI first
        self.dialog_class.show()
        
        # Test long name (over 50 characters)
        long_name = "A" * 51
        self.dialog_class.name_entry.insert(0, long_name)
        is_valid, error = self.dialog_class.validate_form()
        
        self.assertFalse(is_valid)
        self.assertIn("50 characters", error)
        
        # Clean up
        self.dialog_class.dialog.destroy()
    
    def test_validate_form_invalid_characters(self):
        """Test form validation with invalid characters."""
        # Create dialog UI first
        self.dialog_class.show()
        
        # Test invalid characters
        self.dialog_class.name_entry.insert(0, "Test@#$%")
        is_valid, error = self.dialog_class.validate_form()
        
        self.assertFalse(is_valid)
        self.assertIn("invalid characters", error)
        
        # Clean up
        self.dialog_class.dialog.destroy()
    
    def test_validate_form_valid_name(self):
        """Test form validation with valid name."""
        # Create dialog UI first
        self.dialog_class.show()
        
        # Test valid name
        self.dialog_class.name_entry.insert(0, "My Personal Cashbook")
        is_valid, error = self.dialog_class.validate_form()
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Clean up
        self.dialog_class.dialog.destroy()
    
    def test_validate_form_long_description(self):
        """Test form validation with too long description."""
        # Create dialog UI first
        self.dialog_class.show()
        
        # Test valid name but long description
        self.dialog_class.name_entry.insert(0, "Valid Name")
        long_desc = "A" * 201
        self.dialog_class.desc_entry.insert(0, long_desc)
        is_valid, error = self.dialog_class.validate_form()
        
        self.assertFalse(is_valid)
        self.assertIn("200 characters", error)
        
        # Clean up
        self.dialog_class.dialog.destroy()


if __name__ == '__main__':
    unittest.main()
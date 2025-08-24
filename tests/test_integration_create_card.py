"""
Integration tests for CreateCashbookCard with CashbookManager.
"""

import unittest
import tempfile
import shutil
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cashbook_manager import CashbookManager


class TestCreateCashbookCardIntegration(unittest.TestCase):
    """Integration tests for CreateCashbookCard with CashbookManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.manager = CashbookManager(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_create_cashbook_callback_integration(self):
        """Test that the create callback integrates correctly with CashbookManager."""
        # Simulate the callback that would be called by CreateCashbookCard
        def create_callback(name, description, category):
            return self.manager.create_cashbook(
                name=name,
                description=description,
                category=category
            )
        
        # Test creating a cashbook
        cashbook = create_callback("Test Cashbook", "Test Description", "Personal")
        
        # Verify cashbook was created
        self.assertIsNotNone(cashbook)
        self.assertEqual(cashbook.name, "Test Cashbook")
        self.assertEqual(cashbook.description, "Test Description")
        self.assertEqual(cashbook.category, "Personal")
        
        # Verify it appears in recent cashbooks
        recent = self.manager.get_recent_cashbooks()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].name, "Test Cashbook")
    
    def test_create_multiple_cashbooks(self):
        """Test creating multiple cashbooks through the callback."""
        def create_callback(name, description, category):
            return self.manager.create_cashbook(
                name=name,
                description=description,
                category=category
            )
        
        # Create multiple cashbooks
        cashbooks = [
            ("Personal Expenses", "My personal spending", "Personal"),
            ("Business Travel", "Work-related travel expenses", "Business"),
            ("Vacation Fund", "", "Travel")
        ]
        
        created_cashbooks = []
        for name, desc, cat in cashbooks:
            cashbook = create_callback(name, desc, cat)
            created_cashbooks.append(cashbook)
        
        # Verify all were created
        self.assertEqual(len(created_cashbooks), 3)
        
        # Verify they appear in recent cashbooks
        recent = self.manager.get_recent_cashbooks()
        self.assertEqual(len(recent), 3)
        
        # Verify metadata is updated
        metadata = self.manager.get_metadata()
        self.assertEqual(metadata.total_cashbooks, 3)
        self.assertIn("Personal", metadata.categories)
        self.assertIn("Business", metadata.categories)
        self.assertIn("Travel", metadata.categories)
    
    def test_create_cashbook_validation_integration(self):
        """Test that validation errors are properly handled."""
        def create_callback(name, description, category):
            return self.manager.create_cashbook(
                name=name,
                description=description,
                category=category
            )
        
        # Test with invalid name (empty)
        with self.assertRaises(ValueError):
            create_callback("", "Description", "Category")
        
        # Test with invalid name (whitespace only)
        with self.assertRaises(ValueError):
            create_callback("   ", "Description", "Category")
        
        # Test with valid short name (CashbookManager allows 1 character, dialog prevents it)
        cashbook = create_callback("A", "Description", "Category")
        self.assertIsNotNone(cashbook)
        self.assertEqual(cashbook.name, "A")
        
        # Verify one cashbook was created
        recent = self.manager.get_recent_cashbooks()
        self.assertEqual(len(recent), 1)
    
    def test_dashboard_refresh_after_creation(self):
        """Test that dashboard would refresh correctly after cashbook creation."""
        # Simulate initial empty state
        recent = self.manager.get_recent_cashbooks()
        self.assertEqual(len(recent), 0)
        
        # Create a cashbook
        cashbook = self.manager.create_cashbook("New Cashbook", "", "")
        
        # Simulate dashboard refresh
        recent_after = self.manager.get_recent_cashbooks()
        self.assertEqual(len(recent_after), 1)
        self.assertEqual(recent_after[0].id, cashbook.id)


if __name__ == '__main__':
    unittest.main()
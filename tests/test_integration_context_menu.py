"""
Integration tests for context menu functionality.

This module tests the complete context menu workflow including
the interaction between dashboard view and cashbook manager.
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch
try:
    from src.cashbook_manager import CashbookManager
    from src.dashboard_view import DashboardView
except ImportError:
    import sys
    sys.path.append('src')
    from cashbook_manager import CashbookManager
    from dashboard_view import DashboardView


class TestContextMenuIntegration:
    """Integration tests for context menu functionality."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cashbook_manager(self, temp_data_dir):
        """Create a cashbook manager with test data."""
        manager = CashbookManager(data_dir=temp_data_dir)
        
        # Create test cashbooks
        cashbook1 = manager.create_cashbook("Test Cashbook 1", "Description 1", "Personal")
        cashbook2 = manager.create_cashbook("Test Cashbook 2", "Description 2", "Business")
        
        return manager
    
    def test_context_menu_rename_integration(self, cashbook_manager):
        """Test the complete rename workflow."""
        # Get a test cashbook
        cashbooks = cashbook_manager.get_all_cashbooks()
        test_cashbook = cashbooks[0]
        original_name = test_cashbook.name
        new_name = "Renamed Integration Test"
        
        # Create a mock dashboard view with real methods
        dashboard = Mock()
        dashboard.cashbook_manager = cashbook_manager
        dashboard.update_status = Mock()
        dashboard.refresh_cashbooks = Mock()
        
        # Bind the real method
        dashboard.handle_cashbook_rename = DashboardView.handle_cashbook_rename.__get__(dashboard)
        
        # Mock the input dialog and success message
        with patch('customtkinter.CTkInputDialog') as mock_input_dialog, \
             patch('CTkMessagebox.CTkMessagebox') as mock_messagebox:
            
            # Mock input dialog to return new name
            mock_dialog = Mock()
            mock_dialog.get_input.return_value = new_name
            mock_input_dialog.return_value = mock_dialog
            
            # Call rename handler
            dashboard.handle_cashbook_rename(test_cashbook.id)
            
            # Verify cashbook was renamed in the manager
            updated_cashbook = cashbook_manager.get_cashbook(test_cashbook.id)
            assert updated_cashbook is not None
            assert updated_cashbook.name == new_name
            assert updated_cashbook.name != original_name
            
            # Verify UI methods were called
            dashboard.refresh_cashbooks.assert_called_once()
            dashboard.update_status.assert_called()
    
    def test_context_menu_delete_integration(self, cashbook_manager):
        """Test the complete delete workflow."""
        # Get a test cashbook
        cashbooks = cashbook_manager.get_all_cashbooks()
        test_cashbook = cashbooks[0]
        cashbook_id = test_cashbook.id
        cashbook_name = test_cashbook.name
        
        # Verify cashbook exists before deletion
        assert cashbook_manager.get_cashbook(cashbook_id) is not None
        
        # Create a mock dashboard view with real methods
        dashboard = Mock()
        dashboard.cashbook_manager = cashbook_manager
        dashboard.update_status = Mock()
        dashboard.refresh_cashbooks = Mock()
        
        # Bind the real method
        dashboard.handle_cashbook_delete = DashboardView.handle_cashbook_delete.__get__(dashboard)
        
        # Mock the confirmation dialog to confirm deletion
        with patch('CTkMessagebox.CTkMessagebox') as mock_messagebox:
            mock_msg = Mock()
            mock_msg.get.return_value = "Delete"
            mock_messagebox.return_value = mock_msg
            
            # Call delete handler
            dashboard.handle_cashbook_delete(cashbook_id)
            
            # Verify cashbook was deleted from the manager
            deleted_cashbook = cashbook_manager.get_cashbook(cashbook_id)
            assert deleted_cashbook is None
            
            # Verify UI methods were called
            dashboard.refresh_cashbooks.assert_called_once()
            dashboard.update_status.assert_called()
    
    def test_context_menu_cancel_operations(self, cashbook_manager):
        """Test that cancelled operations don't modify data."""
        # Get a test cashbook
        cashbooks = cashbook_manager.get_all_cashbooks()
        test_cashbook = cashbooks[0]
        original_name = test_cashbook.name
        cashbook_id = test_cashbook.id
        
        # Create a mock dashboard view with real methods
        dashboard = Mock()
        dashboard.cashbook_manager = cashbook_manager
        dashboard.update_status = Mock()
        dashboard.refresh_cashbooks = Mock()
        
        # Bind the real methods
        dashboard.handle_cashbook_rename = DashboardView.handle_cashbook_rename.__get__(dashboard)
        dashboard.handle_cashbook_delete = DashboardView.handle_cashbook_delete.__get__(dashboard)
        
        # Test cancelled rename
        with patch('customtkinter.CTkInputDialog') as mock_input_dialog:
            mock_dialog = Mock()
            mock_dialog.get_input.return_value = None  # User cancelled
            mock_input_dialog.return_value = mock_dialog
            
            dashboard.handle_cashbook_rename(cashbook_id)
            
            # Verify cashbook name unchanged
            unchanged_cashbook = cashbook_manager.get_cashbook(cashbook_id)
            assert unchanged_cashbook.name == original_name
        
        # Test cancelled delete
        with patch('CTkMessagebox.CTkMessagebox') as mock_messagebox:
            mock_msg = Mock()
            mock_msg.get.return_value = "Cancel"  # User cancelled
            mock_messagebox.return_value = mock_msg
            
            dashboard.handle_cashbook_delete(cashbook_id)
            
            # Verify cashbook still exists
            existing_cashbook = cashbook_manager.get_cashbook(cashbook_id)
            assert existing_cashbook is not None
            assert existing_cashbook.name == original_name
    
    def test_validation_prevents_invalid_operations(self, cashbook_manager):
        """Test that validation prevents invalid rename operations."""
        # Get test cashbooks
        cashbooks = cashbook_manager.get_all_cashbooks()
        test_cashbook1 = cashbooks[0]
        test_cashbook2 = cashbooks[1]
        
        # Create a mock dashboard view with real methods
        dashboard = Mock()
        dashboard.cashbook_manager = cashbook_manager
        dashboard.update_status = Mock()
        dashboard.refresh_cashbooks = Mock()
        
        # Bind the real method
        dashboard.handle_cashbook_rename = DashboardView.handle_cashbook_rename.__get__(dashboard)
        
        # Test empty name validation (whitespace input is ignored, no error message)
        with patch('customtkinter.CTkInputDialog') as mock_input_dialog:
            
            mock_dialog = Mock()
            mock_dialog.get_input.return_value = "   "  # Empty/whitespace name
            mock_input_dialog.return_value = mock_dialog
            
            original_name = test_cashbook1.name
            dashboard.handle_cashbook_rename(test_cashbook1.id)
            
            # Verify name unchanged (whitespace input is simply ignored)
            unchanged_cashbook = cashbook_manager.get_cashbook(test_cashbook1.id)
            assert unchanged_cashbook.name == original_name
        
        # Test duplicate name validation
        with patch('customtkinter.CTkInputDialog') as mock_input_dialog, \
             patch('CTkMessagebox.CTkMessagebox') as mock_messagebox:
            
            mock_dialog = Mock()
            mock_dialog.get_input.return_value = test_cashbook2.name  # Duplicate name
            mock_input_dialog.return_value = mock_dialog
            
            original_name = test_cashbook1.name
            dashboard.handle_cashbook_rename(test_cashbook1.id)
            
            # Verify name unchanged
            unchanged_cashbook = cashbook_manager.get_cashbook(test_cashbook1.id)
            assert unchanged_cashbook.name == original_name
            
            # Verify error message was shown
            mock_messagebox.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
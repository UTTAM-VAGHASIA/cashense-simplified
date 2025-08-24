"""
Unit tests for the DashboardView component.

Tests the main dashboard interface including layout management,
cashbook display, responsive design, and error handling.
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import customtkinter as ctk
    from models import Cashbook, CashbookMetadata
    from cashbook_manager import CashbookManager
    from dashboard_view import DashboardView
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False


@pytest.mark.skipif(not CUSTOMTKINTER_AVAILABLE, reason="CustomTkinter not available")
class TestDashboardView:
    """Test cases for DashboardView component."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_manager(self):
        """Create a mock cashbook manager."""
        manager = Mock(spec=CashbookManager)
        
        # Create test cashbooks
        cashbooks = []
        for i in range(5):
            cashbook = Cashbook(
                id=f"cb_{i}",
                name=f"Cashbook {i}",
                description=f"Description {i}",
                category="Test"
            )
            cashbooks.append(cashbook)
        
        manager.get_recent_cashbooks.return_value = cashbooks[:3]
        manager.get_all_cashbooks.return_value = cashbooks
        manager._cashbooks = {cb.id: cb for cb in cashbooks}
        
        # Mock metadata
        metadata = CashbookMetadata(
            total_cashbooks=len(cashbooks),
            recent_activity=[cb.id for cb in cashbooks],
            categories=["Test"]
        )
        manager.get_metadata.return_value = metadata
        manager.get_error_recovery_info.return_value = {"has_backups": False}
        
        return manager
    
    @pytest.fixture
    def root_window(self):
        """Create a root window for testing."""
        root = ctk.CTk()
        root.withdraw()  # Hide during testing
        yield root
        root.destroy()
    
    @pytest.fixture
    def dashboard_view(self, root_window, mock_manager):
        """Create a dashboard view for testing."""
        return DashboardView(root_window, mock_manager)
    
    def test_dashboard_initialization(self, dashboard_view, mock_manager):
        """Test dashboard initialization."""
        assert isinstance(dashboard_view, DashboardView)
        assert dashboard_view.cashbook_manager == mock_manager
        assert dashboard_view.parent is not None
        
        # Check layout components
        assert hasattr(dashboard_view, 'header_frame')
        assert hasattr(dashboard_view, 'main_content')
        assert hasattr(dashboard_view, 'footer_frame')
        assert hasattr(dashboard_view, 'grid_frame')
        
        # Check responsive design attributes
        assert hasattr(dashboard_view, 'current_layout_mode')
        assert hasattr(dashboard_view, 'cards_per_row')
        assert dashboard_view.current_layout_mode == "desktop"
        assert dashboard_view.cards_per_row == 2
    
    def test_setup_layout(self, dashboard_view):
        """Test layout setup."""
        # Should have created all layout sections
        assert dashboard_view.header_frame is not None
        assert dashboard_view.main_content is not None
        assert dashboard_view.footer_frame is not None
        assert dashboard_view.grid_frame is not None
        
        # Check grid configuration
        assert dashboard_view.grid_columnconfigure(0)['weight'] == 1
        assert dashboard_view.grid_rowconfigure(1)['weight'] == 1
    
    def test_create_header_section(self, dashboard_view):
        """Test header section creation."""
        header = dashboard_view.header_frame
        
        assert header is not None
        assert header.cget('height') == 80
        
        # Should have title label
        children = header.winfo_children()
        assert len(children) >= 1
        
        # Find title label
        title_labels = [child for child in children if isinstance(child, ctk.CTkLabel)]
        assert len(title_labels) >= 1
    
    def test_create_footer_section(self, dashboard_view):
        """Test footer section creation."""
        footer = dashboard_view.footer_frame
        
        assert footer is not None
        assert footer.cget('height') == 40
        
        # Should have status label
        assert hasattr(dashboard_view, 'status_label')
        assert dashboard_view.status_label is not None
    
    def test_calculate_max_visible_cashbooks(self, dashboard_view):
        """Test max visible cashbooks calculation."""
        # Test desktop mode
        dashboard_view.current_layout_mode = "desktop"
        dashboard_view.cards_per_row = 2
        max_visible = dashboard_view.calculate_max_visible_cashbooks()
        assert max_visible == 4
        
        # Test mobile mode
        dashboard_view.current_layout_mode = "mobile"
        max_visible = dashboard_view.calculate_max_visible_cashbooks()
        assert max_visible == 3
        
        # Test tablet mode
        dashboard_view.current_layout_mode = "tablet"
        dashboard_view.cards_per_row = 1
        max_visible = dashboard_view.calculate_max_visible_cashbooks()
        assert max_visible == 4
        
        # Test desktop with 3 columns
        dashboard_view.current_layout_mode = "desktop"
        dashboard_view.cards_per_row = 3
        max_visible = dashboard_view.calculate_max_visible_cashbooks()
        assert max_visible == 6
    
    def test_refresh_cashbooks_with_data(self, dashboard_view, mock_manager):
        """Test refreshing cashbooks with existing data."""
        # Mock the calculate_max_visible_cashbooks method
        dashboard_view.calculate_max_visible_cashbooks = Mock(return_value=4)
        
        # Refresh cashbooks
        dashboard_view.refresh_cashbooks()
        
        # Should have called manager methods
        mock_manager.get_recent_cashbooks.assert_called()
        mock_manager.get_metadata.assert_called()
    
    def test_refresh_cashbooks_empty_state(self, dashboard_view, mock_manager):
        """Test refreshing cashbooks with no data (empty state)."""
        # Mock empty data
        mock_manager.get_recent_cashbooks.return_value = []
        mock_manager.get_metadata.return_value = CashbookMetadata()
        
        # Refresh cashbooks
        dashboard_view.refresh_cashbooks()
        
        # Should handle empty state
        mock_manager.get_recent_cashbooks.assert_called()
    
    def test_refresh_cashbooks_error_handling(self, dashboard_view, mock_manager):
        """Test error handling during refresh."""
        # Mock an error
        mock_manager.get_recent_cashbooks.side_effect = Exception("Test error")
        
        # Should handle error gracefully
        dashboard_view.refresh_cashbooks()
        
        # Dashboard should still be functional
        assert isinstance(dashboard_view, DashboardView)
    
    def test_show_data_error(self, dashboard_view):
        """Test showing data error state."""
        error_message = "Test error message"
        
        dashboard_view.show_data_error(error_message)
        
        # Should update status
        status_text = dashboard_view.status_label.cget('text')
        assert "Error" in status_text
        assert error_message in status_text
    
    def test_show_empty_state(self, dashboard_view, mock_manager):
        """Test showing empty state."""
        # Mock recovery info
        mock_manager.get_error_recovery_info.return_value = {"has_backups": False}
        
        dashboard_view.show_empty_state()
        
        # Should have create card and empty state message
        children = dashboard_view.grid_frame.winfo_children()
        assert len(children) >= 1  # At least create card
    
    def test_show_empty_state_with_recovery(self, dashboard_view, mock_manager):
        """Test showing empty state with recovery info."""
        # Mock recovery info with backups
        mock_manager.get_error_recovery_info.return_value = {"has_backups": True}
        
        dashboard_view.show_empty_state()
        
        # Should show recovery information
        children = dashboard_view.grid_frame.winfo_children()
        assert len(children) >= 1
    
    def test_display_cashbooks_grid(self, dashboard_view, mock_manager):
        """Test displaying cashbooks in grid."""
        cashbooks = mock_manager.get_recent_cashbooks.return_value
        
        # Mock calculate_max_visible_cashbooks
        dashboard_view.calculate_max_visible_cashbooks = Mock(return_value=4)
        
        dashboard_view.display_cashbooks_grid(cashbooks)
        
        # Should have created cards
        children = dashboard_view.grid_frame.winfo_children()
        assert len(children) >= 1  # At least create card
    
    def test_handle_cashbook_creation(self, dashboard_view, mock_manager):
        """Test handling cashbook creation."""
        # Mock create_cashbook method
        new_cashbook = Cashbook(id="new_id", name="New Cashbook")
        mock_manager.create_cashbook.return_value = new_cashbook
        
        dashboard_view.handle_cashbook_creation("New Cashbook", "Description", "Category")
        
        # Should have called create_cashbook
        mock_manager.create_cashbook.assert_called_once_with(
            "New Cashbook", "Description", "Category"
        )
    
    def test_handle_cashbook_click(self, dashboard_view, mock_manager):
        """Test handling cashbook click."""
        # Mock get_cashbook method
        test_cashbook = Cashbook(id="test_id", name="Test Cashbook")
        mock_manager.get_cashbook.return_value = test_cashbook
        
        dashboard_view.handle_cashbook_click("test_id")
        
        # Should have called get_cashbook
        mock_manager.get_cashbook.assert_called_once_with("test_id")
        
        # Should update status
        status_text = dashboard_view.status_label.cget('text')
        assert "Test Cashbook" in status_text
    
    def test_handle_cashbook_click_not_found(self, dashboard_view, mock_manager):
        """Test handling click on non-existent cashbook."""
        # Mock get_cashbook to return None
        mock_manager.get_cashbook.return_value = None
        
        dashboard_view.handle_cashbook_click("nonexistent_id")
        
        # Should update status with error
        status_text = dashboard_view.status_label.cget('text')
        assert "Error" in status_text
    
    def test_handle_cashbook_rename(self, dashboard_view, mock_manager):
        """Test handling cashbook rename."""
        # Mock get_cashbook and update_cashbook
        test_cashbook = Cashbook(id="test_id", name="Old Name")
        mock_manager.get_cashbook.return_value = test_cashbook
        mock_manager.update_cashbook.return_value = True
        
        # Mock CTkInputDialog
        with patch('customtkinter.CTkInputDialog') as mock_dialog:
            mock_dialog.return_value.get_input.return_value = "New Name"
            
            dashboard_view.handle_cashbook_rename("test_id")
            
            # Should have called update_cashbook
            mock_manager.update_cashbook.assert_called_once_with("test_id", name="New Name")
    
    def test_handle_cashbook_delete(self, dashboard_view, mock_manager):
        """Test handling cashbook deletion."""
        # Mock get_cashbook and delete_cashbook
        test_cashbook = Cashbook(id="test_id", name="Test Cashbook")
        mock_manager.get_cashbook.return_value = test_cashbook
        mock_manager.delete_cashbook.return_value = True
        
        # Mock CTkMessagebox
        with patch('CTkMessagebox.CTkMessagebox') as mock_messagebox:
            mock_messagebox.return_value.get.return_value = "Yes"
            
            dashboard_view.handle_cashbook_delete("test_id")
            
            # Should have called delete_cashbook
            mock_manager.delete_cashbook.assert_called_once_with("test_id")
    
    def test_add_see_all_link(self, dashboard_view):
        """Test adding see all link."""
        total_count = 10
        
        # Mock calculate_max_visible_cashbooks
        dashboard_view.calculate_max_visible_cashbooks = Mock(return_value=4)
        
        dashboard_view.add_see_all_link(total_count)
        
        # Should have created see all button
        assert dashboard_view.see_all_button is not None
        assert dashboard_view.see_all_frame is not None
        
        # Button text should show count
        button_text = dashboard_view.see_all_button.cget('text')
        assert "10" in button_text
    
    def test_show_all_cashbooks(self, dashboard_view):
        """Test showing all cashbooks window."""
        # Mock create_all_cashbooks_window
        dashboard_view.create_all_cashbooks_window = Mock()
        
        dashboard_view.show_all_cashbooks()
        
        # Should have called create_all_cashbooks_window
        dashboard_view.create_all_cashbooks_window.assert_called_once()
    
    def test_update_status(self, dashboard_view):
        """Test updating status message."""
        test_message = "Test status message"
        
        dashboard_view.update_status(test_message)
        
        # Should update status label
        status_text = dashboard_view.status_label.cget('text')
        assert test_message in status_text
    
    def test_configure_grid_layout(self, dashboard_view):
        """Test grid layout configuration."""
        # Should have configure_grid_layout method
        assert hasattr(dashboard_view, 'configure_grid_layout')
        
        # Should be able to call without errors
        dashboard_view.configure_grid_layout()
    
    def test_responsive_design_frame_configure(self, dashboard_view):
        """Test responsive design on frame configure."""
        # Mock configure_grid_layout
        dashboard_view.configure_grid_layout = Mock()
        
        # Create mock event
        mock_event = Mock()
        mock_event.widget = dashboard_view
        
        # Trigger configure event
        dashboard_view._on_frame_configure(mock_event)
        
        # Should schedule grid layout update
        # Note: after_idle is used, so we can't directly test the call
        assert hasattr(dashboard_view, 'configure_grid_layout')
    
    def test_show_recovery_info(self, dashboard_view, mock_manager):
        """Test showing recovery info dialog."""
        # Mock recovery info
        recovery_info = {
            "data_directory": "/test/dir",
            "has_backups": True,
            "backup_directory": "/test/backups",
            "total_cashbooks": 5,
            "available_backups": []
        }
        mock_manager.get_error_recovery_info.return_value = recovery_info
        
        # Mock CTkToplevel to avoid creating actual window
        with patch('customtkinter.CTkToplevel') as mock_toplevel:
            mock_window = Mock()
            mock_toplevel.return_value = mock_window
            
            dashboard_view.show_recovery_info()
            
            # Should have created recovery window
            mock_toplevel.assert_called_once()
    
    def test_error_handling_in_methods(self, dashboard_view, mock_manager):
        """Test error handling in various methods."""
        # Test error in handle_cashbook_creation
        mock_manager.create_cashbook.side_effect = Exception("Creation error")
        
        # Should handle error gracefully
        dashboard_view.handle_cashbook_creation("Test", "Desc", "Cat")
        
        # Status should show error
        status_text = dashboard_view.status_label.cget('text')
        assert "Error" in status_text or "Failed" in status_text
    
    def test_grid_cleanup_on_refresh(self, dashboard_view):
        """Test that grid is properly cleaned up on refresh."""
        # Add some mock widgets to grid
        mock_widget1 = Mock()
        mock_widget2 = Mock()
        
        # Mock winfo_children to return our mock widgets
        dashboard_view.grid_frame.winfo_children = Mock(return_value=[mock_widget1, mock_widget2])
        
        # Refresh should clean up widgets
        dashboard_view.refresh_cashbooks()
        
        # Widgets should have been destroyed
        mock_widget1.destroy.assert_called_once()
        mock_widget2.destroy.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
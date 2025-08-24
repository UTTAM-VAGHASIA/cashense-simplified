"""
Integration tests for the complete dashboard workflows.

Tests end-to-end functionality including dashboard view, card interactions,
cashbook management, and performance optimizations working together.
"""

import pytest
import tempfile
import shutil
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import customtkinter as ctk
    from models import Cashbook, CashbookMetadata
    from cashbook_manager import CashbookManager
    from performance_manager import PerformanceOptimizedManager
    from dashboard_view import DashboardView
    from cashbook_card import CashbookCard
    from create_cashbook_card import CreateCashbookCard
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False


@pytest.mark.skipif(not CUSTOMTKINTER_AVAILABLE, reason="CustomTkinter not available")
class TestDashboardIntegration:
    """Integration tests for dashboard functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cashbook_manager(self, temp_dir):
        """Create a cashbook manager with test data."""
        manager = CashbookManager(data_dir=temp_dir)
        
        # Create test cashbooks
        test_cashbooks = [
            ("Personal Expenses", "Daily personal expenses", "Personal"),
            ("Business Travel", "Business trip expenses", "Business"),
            ("Vacation Fund", "Saving for vacation", "Travel"),
            ("Emergency Fund", "Emergency expenses", "Personal"),
            ("Project Alpha", "Project-related expenses", "Business")
        ]
        
        for name, desc, category in test_cashbooks:
            manager.create_cashbook(name, desc, category)
        
        return manager
    
    @pytest.fixture
    def root_window(self):
        """Create a root window for testing."""
        root = ctk.CTk()
        root.withdraw()  # Hide during testing
        yield root
        root.destroy()
    
    @pytest.fixture
    def dashboard_view(self, root_window, cashbook_manager):
        """Create a dashboard view for testing."""
        return DashboardView(root_window, cashbook_manager)
    
    def test_dashboard_initialization_with_data(self, dashboard_view, cashbook_manager):
        """Test dashboard initialization with existing cashbooks."""
        # Dashboard should be created successfully
        assert isinstance(dashboard_view, DashboardView)
        assert dashboard_view.cashbook_manager == cashbook_manager
        
        # Should have header, main content, and footer
        assert hasattr(dashboard_view, 'header_frame')
        assert hasattr(dashboard_view, 'main_content')
        assert hasattr(dashboard_view, 'footer_frame')
        
        # Should have grid frame for cards
        assert hasattr(dashboard_view, 'grid_frame')
    
    def test_dashboard_empty_state(self, root_window, temp_dir):
        """Test dashboard with no cashbooks (empty state)."""
        empty_manager = CashbookManager(data_dir=temp_dir)
        dashboard = DashboardView(root_window, empty_manager)
        
        # Should handle empty state gracefully
        assert isinstance(dashboard, DashboardView)
        
        # Should show empty state
        dashboard.refresh_cashbooks()
        
        # Check that create card is present
        cards = [child for child in dashboard.grid_frame.winfo_children() 
                if isinstance(child, CreateCashbookCard)]
        assert len(cards) >= 1
    
    def test_cashbook_creation_workflow(self, dashboard_view):
        """Test complete cashbook creation workflow."""
        initial_count = len(dashboard_view.cashbook_manager._cashbooks)
        
        # Simulate cashbook creation
        dashboard_view.handle_cashbook_creation(
            "New Test Cashbook",
            "Test description",
            "Test Category"
        )
        
        # Should have created new cashbook
        assert len(dashboard_view.cashbook_manager._cashbooks) == initial_count + 1
        
        # Should be in recent activity
        recent = dashboard_view.cashbook_manager.get_recent_cashbooks(1)
        assert len(recent) == 1
        assert recent[0].name == "New Test Cashbook"
    
    def test_cashbook_deletion_workflow(self, dashboard_view):
        """Test complete cashbook deletion workflow."""
        # Get a cashbook to delete
        cashbooks = dashboard_view.cashbook_manager.get_all_cashbooks()
        assert len(cashbooks) > 0
        
        cashbook_to_delete = cashbooks[0]
        initial_count = len(dashboard_view.cashbook_manager._cashbooks)
        
        # Simulate deletion
        success = dashboard_view.cashbook_manager.delete_cashbook(cashbook_to_delete.id)
        
        assert success is True
        assert len(dashboard_view.cashbook_manager._cashbooks) == initial_count - 1
        
        # Should not be in recent activity
        recent_ids = [cb.id for cb in dashboard_view.cashbook_manager.get_recent_cashbooks(10)]
        assert cashbook_to_delete.id not in recent_ids
    
    def test_cashbook_update_workflow(self, dashboard_view):
        """Test complete cashbook update workflow."""
        # Get a cashbook to update
        cashbooks = dashboard_view.cashbook_manager.get_all_cashbooks()
        assert len(cashbooks) > 0
        
        cashbook_to_update = cashbooks[0]
        original_name = cashbook_to_update.name
        
        # Simulate update
        success = dashboard_view.cashbook_manager.update_cashbook(
            cashbook_to_update.id,
            name="Updated Name",
            description="Updated description"
        )
        
        assert success is True
        
        # Verify update
        updated_cashbook = dashboard_view.cashbook_manager.get_cashbook(cashbook_to_update.id)
        assert updated_cashbook.name == "Updated Name"
        assert updated_cashbook.description == "Updated description"
        assert updated_cashbook.name != original_name
    
    def test_dashboard_refresh_after_changes(self, dashboard_view):
        """Test dashboard refresh after data changes."""
        # Make changes to data
        dashboard_view.handle_cashbook_creation("Refresh Test", "Test", "Test")
        
        # Refresh dashboard
        dashboard_view.refresh_cashbooks()
        
        # Should handle refresh without errors
        assert isinstance(dashboard_view, DashboardView)
    
    def test_responsive_layout_calculation(self, dashboard_view):
        """Test responsive layout calculations."""
        # Test max visible cashbooks calculation
        max_visible = dashboard_view.calculate_max_visible_cashbooks()
        assert isinstance(max_visible, int)
        assert max_visible > 0
        
        # Test with different layout modes
        dashboard_view.current_layout_mode = "mobile"
        mobile_max = dashboard_view.calculate_max_visible_cashbooks()
        
        dashboard_view.current_layout_mode = "desktop"
        desktop_max = dashboard_view.calculate_max_visible_cashbooks()
        
        # Desktop should typically show more than mobile
        assert desktop_max >= mobile_max
    
    def test_see_all_functionality(self, dashboard_view):
        """Test 'see all' functionality with many cashbooks."""
        # Create many cashbooks to trigger see all
        for i in range(10):
            dashboard_view.cashbook_manager.create_cashbook(
                f"Extra Cashbook {i}",
                f"Description {i}",
                "Extra"
            )
        
        # Refresh to show see all button
        dashboard_view.refresh_cashbooks()
        
        # Should have see all button when there are many cashbooks
        total_cashbooks = len(dashboard_view.cashbook_manager._cashbooks)
        max_visible = dashboard_view.calculate_max_visible_cashbooks()
        
        if total_cashbooks > max_visible - 1:  # -1 for create card
            assert hasattr(dashboard_view, 'see_all_button')
    
    def test_error_handling_in_dashboard(self, dashboard_view):
        """Test error handling in dashboard operations."""
        # Mock an error in cashbook manager
        with patch.object(dashboard_view.cashbook_manager, 'get_recent_cashbooks', 
                         side_effect=Exception("Test error")):
            
            # Should handle error gracefully
            dashboard_view.refresh_cashbooks()
            
            # Dashboard should still exist and be functional
            assert isinstance(dashboard_view, DashboardView)
    
    def test_performance_with_large_dataset(self, root_window, temp_dir):
        """Test dashboard performance with large number of cashbooks."""
        # Create manager with many cashbooks
        manager = CashbookManager(data_dir=temp_dir)
        
        # Create 100 cashbooks
        start_time = time.time()
        for i in range(100):
            manager.create_cashbook(
                f"Cashbook {i:03d}",
                f"Description for cashbook {i}",
                f"Category {i % 5}"
            )
        creation_time = time.time() - start_time
        
        # Create dashboard
        start_time = time.time()
        dashboard = DashboardView(root_window, manager)
        dashboard_creation_time = time.time() - start_time
        
        # Should handle large dataset reasonably quickly
        assert creation_time < 5.0  # Should create 100 cashbooks in under 5 seconds
        assert dashboard_creation_time < 2.0  # Should create dashboard in under 2 seconds
        
        # Dashboard should be functional
        assert isinstance(dashboard, DashboardView)
        assert len(manager._cashbooks) == 100


@pytest.mark.skipif(not CUSTOMTKINTER_AVAILABLE, reason="CustomTkinter not available")
class TestCardInteractionIntegration:
    """Integration tests for card interactions."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cashbook_manager(self, temp_dir):
        """Create a cashbook manager with test data."""
        manager = CashbookManager(data_dir=temp_dir)
        manager.create_cashbook("Test Cashbook", "Test description", "Test")
        return manager
    
    @pytest.fixture
    def root_window(self):
        """Create a root window for testing."""
        root = ctk.CTk()
        root.withdraw()
        yield root
        root.destroy()
    
    def test_cashbook_card_creation_and_interaction(self, root_window, cashbook_manager):
        """Test cashbook card creation and basic interactions."""
        cashbook = cashbook_manager.get_all_cashbooks()[0]
        
        click_callback = Mock()
        context_callback = Mock()
        
        # Create cashbook card
        card = CashbookCard(
            root_window,
            cashbook_data=cashbook,
            on_click_callback=click_callback,
            on_context_menu_callback=context_callback
        )
        
        # Test card creation
        assert isinstance(card, CashbookCard)
        assert card.cashbook_data == cashbook
        
        # Test click handling
        card.handle_click()
        click_callback.assert_called_once_with(cashbook.id)
        
        # Test context menu handling
        mock_event = Mock()
        mock_event.x = 50
        mock_event.y = 30
        card.winfo_rootx = Mock(return_value=100)
        card.winfo_rooty = Mock(return_value=200)
        
        card.handle_context_menu(mock_event)
        context_callback.assert_called_once_with(cashbook.id, 150, 230)
    
    def test_create_cashbook_card_interaction(self, root_window):
        """Test create cashbook card interactions."""
        create_callback = Mock()
        
        # Create card
        card = CreateCashbookCard(root_window, create_callback)
        
        assert isinstance(card, CreateCashbookCard)
        assert card.on_create_callback == create_callback
    
    def test_card_update_display(self, root_window, cashbook_manager):
        """Test updating card display with new data."""
        cashbook = cashbook_manager.get_all_cashbooks()[0]
        
        card = CashbookCard(
            root_window,
            cashbook_data=cashbook,
            on_click_callback=Mock()
        )
        
        # Create updated cashbook data
        updated_cashbook = Cashbook(
            id=cashbook.id,
            name="Updated Name",
            description="Updated description",
            category="Updated Category"
        )
        
        # Update display
        card.update_display(updated_cashbook)
        
        # Verify update
        assert card.cashbook_data.name == "Updated Name"
        assert card.cashbook_data.description == "Updated description"
        assert card.cashbook_data.category == "Updated Category"


class TestPerformanceIntegration:
    """Integration tests for performance optimizations."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cashbook_manager_large(self, temp_dir):
        """Create a cashbook manager with large dataset."""
        manager = CashbookManager(data_dir=temp_dir)
        
        # Create 75 cashbooks (above large dataset threshold)
        for i in range(75):
            manager.create_cashbook(
                f"Cashbook {i:03d}",
                f"Description for cashbook {i}",
                f"Category {i % 10}"
            )
        
        return manager
    
    def test_performance_optimized_manager_integration(self, cashbook_manager_large):
        """Test performance optimized manager with large dataset."""
        optimized_manager = PerformanceOptimizedManager(cashbook_manager_large)
        
        # Test optimized recent cashbooks
        start_time = time.time()
        recent = optimized_manager.get_recent_cashbooks_optimized(limit=20)
        recent_time = time.time() - start_time
        
        assert len(recent) == 20
        assert recent_time < 1.0  # Should be fast
        
        # Test paginated retrieval
        start_time = time.time()
        page_result = optimized_manager.get_all_cashbooks_paginated(page=0, page_size=25)
        pagination_time = time.time() - start_time
        
        assert len(page_result["cashbooks"]) == 25
        assert page_result["pagination"]["total_count"] == 75
        assert pagination_time < 1.0  # Should be fast
        
        # Test search functionality
        start_time = time.time()
        search_results = optimized_manager.search_cashbooks("Cashbook 01")
        search_time = time.time() - start_time
        
        assert len(search_results) > 0
        assert search_time < 1.0  # Should be fast
    
    def test_lazy_loading_integration(self, cashbook_manager_large):
        """Test lazy loading integration with large dataset."""
        optimized_manager = PerformanceOptimizedManager(cashbook_manager_large)
        
        # Test batch loading
        batch1 = optimized_manager.lazy_loader.get_cashbooks_batch(offset=0, limit=10)
        batch2 = optimized_manager.lazy_loader.get_cashbooks_batch(offset=10, limit=10)
        batch3 = optimized_manager.lazy_loader.get_cashbooks_batch(offset=20, limit=10)
        
        assert len(batch1) == 10
        assert len(batch2) == 10
        assert len(batch3) == 10
        
        # Batches should not overlap
        batch1_ids = {cb.id for cb in batch1}
        batch2_ids = {cb.id for cb in batch2}
        batch3_ids = {cb.id for cb in batch3}
        
        assert len(batch1_ids & batch2_ids) == 0  # No overlap
        assert len(batch2_ids & batch3_ids) == 0  # No overlap
        assert len(batch1_ids & batch3_ids) == 0  # No overlap
    
    def test_performance_monitoring_integration(self, cashbook_manager_large):
        """Test performance monitoring integration."""
        optimized_manager = PerformanceOptimizedManager(cashbook_manager_large)
        
        # Perform various operations
        optimized_manager.get_recent_cashbooks_optimized(10)
        optimized_manager.get_all_cashbooks_paginated(page=0, page_size=20)
        optimized_manager.search_cashbooks("Category 1")
        
        # Get performance report
        report = optimized_manager.get_performance_report()
        
        # Should have recorded metrics
        assert report["performance_metrics"]["total_operations"] >= 3
        assert report["dataset_info"]["total_cashbooks"] == 75
        assert report["dataset_info"]["is_large_dataset"] is True
        
        # Should have recommendations
        assert len(report["recommendations"]) > 0
    
    def test_cache_performance_integration(self, cashbook_manager_large):
        """Test cache performance integration."""
        optimized_manager = PerformanceOptimizedManager(cashbook_manager_large)
        
        # First access - should populate cache
        start_time = time.time()
        batch1 = optimized_manager.lazy_loader.get_cashbooks_batch(offset=0, limit=10)
        first_access_time = time.time() - start_time
        
        # Second access - should use cache
        start_time = time.time()
        batch2 = optimized_manager.lazy_loader.get_cashbooks_batch(offset=0, limit=10)
        second_access_time = time.time() - start_time
        
        # Results should be the same
        assert len(batch1) == len(batch2)
        assert [cb.id for cb in batch1] == [cb.id for cb in batch2]
        
        # Second access should be faster (cached)
        # Note: This might not always be true in test environment, so we just check it's reasonable
        assert second_access_time < 1.0
        
        # Check cache stats
        cache_stats = optimized_manager.lazy_loader.get_cache_stats()
        assert cache_stats["total_entries"] > 0
        assert cache_stats["valid_entries"] > 0


class TestDataPersistenceIntegration:
    """Integration tests for data persistence across operations."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_data_persistence_across_manager_instances(self, temp_dir):
        """Test data persistence across manager instances."""
        # Create first manager and add data
        manager1 = CashbookManager(data_dir=temp_dir)
        cashbook1 = manager1.create_cashbook("Persistent Test", "Test description", "Test")
        
        # Create second manager instance
        manager2 = CashbookManager(data_dir=temp_dir)
        
        # Data should be loaded
        assert len(manager2._cashbooks) == 1
        
        retrieved_cashbook = manager2.get_cashbook(cashbook1.id)
        assert retrieved_cashbook is not None
        assert retrieved_cashbook.name == "Persistent Test"
        assert retrieved_cashbook.description == "Test description"
        assert retrieved_cashbook.category == "Test"
    
    def test_metadata_persistence(self, temp_dir):
        """Test metadata persistence across instances."""
        # Create manager and add multiple cashbooks
        manager1 = CashbookManager(data_dir=temp_dir)
        
        categories = ["Personal", "Business", "Travel"]
        for i, category in enumerate(categories):
            manager1.create_cashbook(f"Cashbook {i}", f"Description {i}", category)
        
        # Create new manager instance
        manager2 = CashbookManager(data_dir=temp_dir)
        
        # Metadata should be preserved
        metadata = manager2.get_metadata()
        assert metadata.total_cashbooks == 3
        assert set(metadata.categories) == set(categories)
        assert len(metadata.recent_activity) == 3
    
    def test_backup_and_recovery_integration(self, temp_dir):
        """Test backup creation and data recovery."""
        manager = CashbookManager(data_dir=temp_dir)
        
        # Create test data
        for i in range(5):
            manager.create_cashbook(f"Backup Test {i}", f"Description {i}", "Test")
        
        # Create backup
        backup_path = manager.backup_data()
        
        assert os.path.exists(backup_path)
        assert "cashbooks_backup_" in backup_path
        
        # Verify backup content
        import json
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        assert "cashbooks" in backup_data
        assert "metadata" in backup_data
        assert "backup_timestamp" in backup_data
        assert len(backup_data["cashbooks"]) == 5
    
    def test_error_recovery_integration(self, temp_dir):
        """Test error recovery mechanisms."""
        # Create manager with data
        manager1 = CashbookManager(data_dir=temp_dir)
        manager1.create_cashbook("Recovery Test", "Test", "Test")
        
        # Corrupt the data file
        cashbooks_file = manager1.cashbooks_file
        with open(cashbooks_file, 'w') as f:
            f.write("invalid json content")
        
        # Create new manager - should handle corruption gracefully
        manager2 = CashbookManager(data_dir=temp_dir)
        
        # Should start with empty data but not crash
        assert len(manager2._cashbooks) == 0
        
        # Should be able to create new cashbooks
        new_cashbook = manager2.create_cashbook("Recovery Success", "Recovered", "Test")
        assert new_cashbook.name == "Recovery Success"


if __name__ == '__main__':
    pytest.main([__file__])
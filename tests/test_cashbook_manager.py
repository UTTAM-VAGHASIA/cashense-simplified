"""
Unit tests for the CashbookManager class.

Tests CRUD operations, data persistence, error handling,
and metadata management functionality.
"""

import pytest
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open

from src.cashbook_manager import CashbookManager, FileOperationError, DataCorruptionError
from src.models import Cashbook, CashbookMetadata


class TestCashbookManager:
    """Test cases for the CashbookManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create a CashbookManager instance with temporary directory."""
        return CashbookManager(data_dir=temp_dir)
    
    def test_manager_initialization(self, temp_dir):
        """Test manager initialization creates necessary directories."""
        manager = CashbookManager(data_dir=temp_dir)
        
        assert manager.data_dir == Path(temp_dir)
        assert manager.data_dir.exists()
        assert manager.cashbooks_file == Path(temp_dir) / "cashbooks.json"
        assert manager.metadata_file == Path(temp_dir) / "metadata.json"
        assert isinstance(manager._cashbooks, dict)
        assert isinstance(manager._metadata, CashbookMetadata)
    
    def test_manager_initialization_default_dir(self):
        """Test manager initialization with default directory."""
        with patch('pathlib.Path.home') as mock_home, \
             patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_home.return_value = Path("/fake/home")
            
            manager = CashbookManager()
            
            expected_dir = Path("/fake/home") / ".cashense"
            assert manager.data_dir == expected_dir
            mock_mkdir.assert_called_once_with(exist_ok=True)
    
    def test_create_cashbook_valid(self, manager):
        """Test creating a valid cashbook."""
        cashbook = manager.create_cashbook(
            name="Test Cashbook",
            description="A test cashbook",
            category="Personal"
        )
        
        assert isinstance(cashbook, Cashbook)
        assert cashbook.name == "Test Cashbook"
        assert cashbook.description == "A test cashbook"
        assert cashbook.category == "Personal"
        assert cashbook.id in manager._cashbooks
        assert manager._metadata.total_cashbooks == 1
        assert cashbook.id in manager._metadata.recent_activity
    
    def test_create_cashbook_minimal(self, manager):
        """Test creating a cashbook with minimal data."""
        cashbook = manager.create_cashbook(name="Test")
        
        assert cashbook.name == "Test"
        assert cashbook.description == ""
        assert cashbook.category == ""
        assert cashbook.id in manager._cashbooks
    
    def test_create_cashbook_invalid_name(self, manager):
        """Test creating a cashbook with invalid name."""
        with pytest.raises(ValueError):
            manager.create_cashbook(name="")
    
    def test_get_recent_cashbooks_empty(self, manager):
        """Test getting recent cashbooks when none exist."""
        recent = manager.get_recent_cashbooks()
        assert recent == []
    
    def test_get_recent_cashbooks_with_data(self, manager):
        """Test getting recent cashbooks with existing data."""
        # Create multiple cashbooks
        cb1 = manager.create_cashbook("Cashbook 1")
        cb2 = manager.create_cashbook("Cashbook 2")
        cb3 = manager.create_cashbook("Cashbook 3")
        
        recent = manager.get_recent_cashbooks(limit=2)
        
        assert len(recent) == 2
        # Most recent should be first (cb3, then cb2)
        assert recent[0].id == cb3.id
        assert recent[1].id == cb2.id
    
    def test_get_recent_cashbooks_limit(self, manager):
        """Test that recent cashbooks respects the limit."""
        # Create 5 cashbooks
        for i in range(5):
            manager.create_cashbook(f"Cashbook {i}")
        
        recent = manager.get_recent_cashbooks(limit=3)
        assert len(recent) == 3
    
    def test_get_all_cashbooks_empty(self, manager):
        """Test getting all cashbooks when none exist."""
        all_cashbooks = manager.get_all_cashbooks()
        assert all_cashbooks == []
    
    def test_get_all_cashbooks_with_data(self, manager):
        """Test getting all cashbooks with existing data."""
        cb1 = manager.create_cashbook("Cashbook 1")
        cb2 = manager.create_cashbook("Cashbook 2")
        
        all_cashbooks = manager.get_all_cashbooks()
        
        assert len(all_cashbooks) == 2
        # Should be sorted by last_modified (newest first)
        assert all_cashbooks[0].last_modified >= all_cashbooks[1].last_modified
    
    def test_get_cashbook_existing(self, manager):
        """Test getting an existing cashbook by ID."""
        created = manager.create_cashbook("Test Cashbook")
        retrieved = manager.get_cashbook(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
    
    def test_get_cashbook_nonexistent(self, manager):
        """Test getting a non-existent cashbook."""
        result = manager.get_cashbook("nonexistent-id")
        assert result is None
    
    def test_update_cashbook_existing(self, manager):
        """Test updating an existing cashbook."""
        cashbook = manager.create_cashbook("Original Name")
        original_modified = cashbook.last_modified
        
        # Wait a bit to ensure different timestamp
        import time
        time.sleep(0.01)
        
        success = manager.update_cashbook(
            cashbook.id,
            name="Updated Name",
            description="Updated description",
            category="Updated category"
        )
        
        assert success is True
        
        updated = manager.get_cashbook(cashbook.id)
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        assert updated.category == "Updated category"
        assert updated.last_modified > original_modified
        
        # Should be moved to front of recent activity
        assert manager._metadata.recent_activity[0] == cashbook.id
    
    def test_update_cashbook_nonexistent(self, manager):
        """Test updating a non-existent cashbook."""
        success = manager.update_cashbook("nonexistent-id", name="New Name")
        assert success is False
    
    def test_update_cashbook_invalid_data(self, manager):
        """Test updating a cashbook with invalid data."""
        cashbook = manager.create_cashbook("Test")
        
        with pytest.raises(ValueError):
            manager.update_cashbook(cashbook.id, name="")
    
    def test_delete_cashbook_existing(self, manager):
        """Test deleting an existing cashbook."""
        cashbook = manager.create_cashbook("To Delete")
        
        success = manager.delete_cashbook(cashbook.id)
        
        assert success is True
        assert cashbook.id not in manager._cashbooks
        assert cashbook.id not in manager._metadata.recent_activity
        assert manager._metadata.total_cashbooks == 0
    
    def test_delete_cashbook_nonexistent(self, manager):
        """Test deleting a non-existent cashbook."""
        success = manager.delete_cashbook("nonexistent-id")
        assert success is False
    
    def test_get_cashbook_stats_existing(self, manager):
        """Test getting stats for an existing cashbook."""
        cashbook = manager.create_cashbook(
            name="Test Cashbook",
            category="Personal"
        )
        
        stats = manager.get_cashbook_stats(cashbook.id)
        
        assert stats is not None
        assert stats["id"] == cashbook.id
        assert stats["name"] == "Test Cashbook"
        assert stats["entry_count"] == 0
        assert stats["total_amount"] == 0.0
        assert stats["category"] == "Personal"
        assert "created_date" in stats
        assert "last_modified" in stats
    
    def test_get_cashbook_stats_nonexistent(self, manager):
        """Test getting stats for a non-existent cashbook."""
        stats = manager.get_cashbook_stats("nonexistent-id")
        assert stats is None
    
    def test_get_metadata(self, manager):
        """Test getting metadata."""
        # Create some cashbooks to populate metadata
        manager.create_cashbook("Test 1", category="Personal")
        manager.create_cashbook("Test 2", category="Business")
        
        metadata = manager.get_metadata()
        
        assert isinstance(metadata, CashbookMetadata)
        assert metadata.total_cashbooks == 2
        assert len(metadata.recent_activity) == 2
        assert "Personal" in metadata.categories
        assert "Business" in metadata.categories
    
    def test_backup_data(self, manager):
        """Test creating a backup of data."""
        # Create some test data
        manager.create_cashbook("Test Cashbook", description="Test")
        
        backup_path = manager.backup_data()
        
        assert Path(backup_path).exists()
        assert "cashbooks_backup_" in backup_path
        assert backup_path.endswith(".json")
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        assert "cashbooks" in backup_data
        assert "metadata" in backup_data
        assert "backup_timestamp" in backup_data
        assert len(backup_data["cashbooks"]) == 1
    
    def test_data_persistence(self, temp_dir):
        """Test that data persists across manager instances."""
        # Create manager and add data
        manager1 = CashbookManager(data_dir=temp_dir)
        cashbook = manager1.create_cashbook("Persistent Cashbook", category="Test")
        
        # Create new manager instance
        manager2 = CashbookManager(data_dir=temp_dir)
        
        # Data should be loaded
        assert len(manager2._cashbooks) == 1
        assert manager2._metadata.total_cashbooks == 1
        
        retrieved = manager2.get_cashbook(cashbook.id)
        assert retrieved is not None
        assert retrieved.name == "Persistent Cashbook"
        assert retrieved.category == "Test"
    
    def test_metadata_update_categories(self, manager):
        """Test that metadata categories are updated correctly."""
        manager.create_cashbook("CB1", category="Personal")
        manager.create_cashbook("CB2", category="Business")
        manager.create_cashbook("CB3", category="Personal")  # Duplicate
        manager.create_cashbook("CB4", category="")  # Empty
        
        metadata = manager.get_metadata()
        
        # Should have unique categories, sorted
        assert metadata.categories == ["Business", "Personal"]
    
    def test_recent_activity_limit(self, manager):
        """Test that recent activity is limited to 10 items."""
        # Create 15 cashbooks
        cashbook_ids = []
        for i in range(15):
            cb = manager.create_cashbook(f"Cashbook {i}")
            cashbook_ids.append(cb.id)
        
        # Should only keep last 10
        assert len(manager._metadata.recent_activity) == 10
        
        # Should be the most recent 10 (in reverse order)
        expected_ids = cashbook_ids[-10:][::-1]  # Last 10, reversed
        assert manager._metadata.recent_activity == expected_ids
    
    def test_corrupted_data_handling(self, temp_dir):
        """Test handling of corrupted data files."""
        # Create corrupted cashbooks file
        cashbooks_file = Path(temp_dir) / "cashbooks.json"
        with open(cashbooks_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle gracefully and create backup
        manager = CashbookManager(data_dir=temp_dir)
        
        # Should start with empty data
        assert len(manager._cashbooks) == 0
        assert manager._metadata.total_cashbooks == 0
        
        # Should create backup file in corrupted_backups directory
        backup_dir = Path(temp_dir) / "corrupted_backups"
        if backup_dir.exists():
            backup_files = list(backup_dir.glob("cashbooks_corrupted_*.json"))
            assert len(backup_files) == 1
    
    @patch('tempfile.NamedTemporaryFile', side_effect=OSError("Permission denied"))
    def test_save_data_failure(self, mock_temp_file, manager):
        """Test handling of save operation failures."""
        with pytest.raises(FileOperationError, match="Failed to save cashbook"):
            manager.create_cashbook("Test")
    
    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_backup_failure(self, mock_open_func, manager):
        """Test handling of backup operation failures."""
        with pytest.raises(RuntimeError, match="Failed to create backup"):
            manager.backup_data()
    
    def test_update_recent_activity_existing_item(self, manager):
        """Test that updating an existing cashbook moves it to front of recent activity."""
        # Create multiple cashbooks
        cb1 = manager.create_cashbook("Cashbook 1")
        cb2 = manager.create_cashbook("Cashbook 2")
        cb3 = manager.create_cashbook("Cashbook 3")
        
        # Initial order should be [cb3, cb2, cb1]
        assert manager._metadata.recent_activity == [cb3.id, cb2.id, cb1.id]
        
        # Update cb1 - should move to front
        manager.update_cashbook(cb1.id, description="Updated")
        
        # Order should now be [cb1, cb3, cb2]
        assert manager._metadata.recent_activity == [cb1.id, cb3.id, cb2.id]
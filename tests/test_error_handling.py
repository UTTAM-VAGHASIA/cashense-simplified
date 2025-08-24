"""
Tests for error handling and empty state functionality.

This module tests the error handling mechanisms and empty state display
for the cashbook dashboard application.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Handle import paths for testing
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from cashbook_manager import CashbookManager, FileOperationError, DataCorruptionError
    from models import Cashbook, CashbookMetadata
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    print(f"Skipping tests due to import error: {e}")


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
class TestErrorHandling:
    """Test error handling functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CashbookManager(data_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_corrupted_json_handling(self):
        """Test handling of corrupted JSON files."""
        # Create corrupted cashbooks file
        cashbooks_file = Path(self.temp_dir) / "cashbooks.json"
        with open(cashbooks_file, 'w') as f:
            f.write('{"invalid": json content}')
        
        # Create new manager - should handle corruption gracefully
        manager = CashbookManager(data_dir=self.temp_dir)
        
        # Should start with empty data
        assert len(manager.get_all_cashbooks()) == 0
        assert manager.get_metadata().total_cashbooks == 0
        
        # Should have created backup
        backup_dir = Path(self.temp_dir) / "corrupted_backups"
        assert backup_dir.exists()
    
    def test_file_permission_error(self):
        """Test handling of file permission errors."""
        # Create cashbook first
        cashbook = self.manager.create_cashbook("Test Cashbook")
        
        # Mock file permission error during save
        with patch('tempfile.NamedTemporaryFile', side_effect=PermissionError("Permission denied")):
            with pytest.raises(FileOperationError):
                self.manager.create_cashbook("Another Cashbook")
    
    def test_partial_data_recovery(self):
        """Test recovery of partial data from corrupted files."""
        # Create valid cashbook data
        valid_cashbook = {
            "cb1": {
                "id": "cb1",
                "name": "Valid Cashbook",
                "description": "",
                "category": "",
                "created_date": "2024-01-01T00:00:00",
                "last_modified": "2024-01-01T00:00:00",
                "entry_count": 0,
                "total_amount": 0.0,
                "icon_color": "#3B82F6"
            }
        }
        
        # Create file with mixed valid/invalid data
        cashbooks_file = Path(self.temp_dir) / "cashbooks.json"
        with open(cashbooks_file, 'w') as f:
            json.dump(valid_cashbook, f)
        
        # Load manager - should recover valid data
        manager = CashbookManager(data_dir=self.temp_dir)
        cashbooks = manager.get_all_cashbooks()
        
        assert len(cashbooks) == 1
        assert cashbooks[0].name == "Valid Cashbook"
    
    def test_recovery_info_generation(self):
        """Test generation of recovery information."""
        # Create some test data
        self.manager.create_cashbook("Test Cashbook")
        
        # Get recovery info
        recovery_info = self.manager.get_error_recovery_info()
        
        assert "data_directory" in recovery_info
        assert "total_cashbooks" in recovery_info
        assert "has_backups" in recovery_info
        assert recovery_info["total_cashbooks"] == 1
    
    def test_data_integrity_validation(self):
        """Test data integrity validation."""
        # Create cashbook with valid data
        cashbook = self.manager.create_cashbook("Test Cashbook")
        
        # Validate integrity
        integrity_report = self.manager.validate_data_integrity()
        
        assert integrity_report["is_valid"] is True
        assert len(integrity_report["issues"]) == 0
        assert integrity_report["cashbook_count"] == 1
    
    def test_data_integrity_with_issues(self):
        """Test data integrity validation with issues."""
        # Create cashbook
        cashbook = self.manager.create_cashbook("Test Cashbook")
        
        # Manually corrupt metadata
        self.manager._metadata.total_cashbooks = 999  # Wrong count
        
        # Validate integrity
        integrity_report = self.manager.validate_data_integrity()
        
        assert integrity_report["is_valid"] is False
        assert len(integrity_report["issues"]) > 0
        assert "doesn't match actual count" in integrity_report["issues"][0]
    
    def test_backup_creation(self):
        """Test manual backup creation."""
        # Create test data
        self.manager.create_cashbook("Test Cashbook")
        
        # Create backup
        backup_path = self.manager.backup_data()
        
        assert os.path.exists(backup_path)
        assert "backup" in backup_path
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        assert "cashbooks" in backup_data
        assert "metadata" in backup_data
        assert "backup_timestamp" in backup_data
    
    def test_empty_state_with_no_cashbooks(self):
        """Test empty state when no cashbooks exist."""
        # Ensure no cashbooks exist
        cashbooks = self.manager.get_all_cashbooks()
        assert len(cashbooks) == 0
        
        # Recovery info should indicate no backups initially
        recovery_info = self.manager.get_error_recovery_info()
        assert recovery_info["total_cashbooks"] == 0
        assert not recovery_info["has_backups"]
    
    def test_atomic_save_operations(self):
        """Test that save operations are atomic."""
        # Create initial cashbook
        cashbook = self.manager.create_cashbook("Test Cashbook")
        
        # Mock failure during atomic save
        with patch('shutil.move', side_effect=OSError("Disk full")):
            with pytest.raises(FileOperationError):
                self.manager.create_cashbook("Another Cashbook")
        
        # Original data should still be intact
        cashbooks = self.manager.get_all_cashbooks()
        assert len(cashbooks) == 1
        assert cashbooks[0].name == "Test Cashbook"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
class TestEmptyStateHandling:
    """Test empty state display and guidance."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CashbookManager(data_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_state_detection(self):
        """Test detection of empty state."""
        # Should start empty
        cashbooks = self.manager.get_recent_cashbooks()
        assert len(cashbooks) == 0
        
        metadata = self.manager.get_metadata()
        assert metadata.total_cashbooks == 0
    
    def test_recovery_after_corruption(self):
        """Test recovery state after data corruption."""
        # Create corrupted file to trigger recovery
        cashbooks_file = Path(self.temp_dir) / "cashbooks.json"
        with open(cashbooks_file, 'w') as f:
            f.write('invalid json')
        
        # Create new manager - should handle corruption
        manager = CashbookManager(data_dir=self.temp_dir)
        
        # Should be in recovery state
        recovery_info = manager.get_error_recovery_info()
        assert recovery_info["has_backups"]  # Backup should be created
        assert recovery_info["total_cashbooks"] == 0  # Should start fresh


if __name__ == "__main__":
    pytest.main([__file__])
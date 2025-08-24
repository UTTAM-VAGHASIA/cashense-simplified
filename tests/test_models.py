"""
Unit tests for the data models module.

Tests the Cashbook and CashbookMetadata dataclasses including
validation, serialization, and deserialization functionality.
"""

import pytest
from datetime import datetime
from src.models import Cashbook, CashbookMetadata, generate_cashbook_id


class TestCashbook:
    """Test cases for the Cashbook dataclass."""
    
    def test_cashbook_creation_valid(self):
        """Test creating a valid cashbook."""
        cashbook = Cashbook(
            id="test-id",
            name="Test Cashbook",
            description="A test cashbook",
            category="Personal"
        )
        
        assert cashbook.id == "test-id"
        assert cashbook.name == "Test Cashbook"
        assert cashbook.description == "A test cashbook"
        assert cashbook.category == "Personal"
        assert cashbook.entry_count == 0
        assert cashbook.total_amount == 0.0
        assert cashbook.icon_color == "#3B82F6"
        assert isinstance(cashbook.created_date, datetime)
        assert isinstance(cashbook.last_modified, datetime)
    
    def test_cashbook_creation_minimal(self):
        """Test creating a cashbook with minimal required fields."""
        cashbook = Cashbook(id="test-id", name="Test")
        
        assert cashbook.id == "test-id"
        assert cashbook.name == "Test"
        assert cashbook.description == ""
        assert cashbook.category == ""
    
    def test_cashbook_name_validation_empty(self):
        """Test that empty names are rejected."""
        with pytest.raises(ValueError, match="Cashbook name cannot be empty"):
            Cashbook(id="test-id", name="")
    
    def test_cashbook_name_validation_whitespace(self):
        """Test that whitespace-only names are rejected."""
        with pytest.raises(ValueError, match="Cashbook name cannot be empty"):
            Cashbook(id="test-id", name="   ")
    
    def test_cashbook_name_validation_too_long(self):
        """Test that names exceeding 100 characters are rejected."""
        long_name = "a" * 101
        with pytest.raises(ValueError, match="Cashbook name cannot exceed 100 characters"):
            Cashbook(id="test-id", name=long_name)
    
    def test_cashbook_name_trimming(self):
        """Test that names are trimmed of whitespace."""
        cashbook = Cashbook(id="test-id", name="  Test Name  ")
        assert cashbook.name == "Test Name"
    
    def test_cashbook_entry_count_validation(self):
        """Test that negative entry counts are rejected."""
        with pytest.raises(ValueError, match="Entry count cannot be negative"):
            Cashbook(id="test-id", name="Test", entry_count=-1)
    
    def test_cashbook_to_dict(self):
        """Test converting cashbook to dictionary."""
        created_date = datetime(2023, 1, 1, 12, 0, 0)
        modified_date = datetime(2023, 1, 2, 12, 0, 0)
        
        cashbook = Cashbook(
            id="test-id",
            name="Test Cashbook",
            description="Test description",
            category="Personal",
            created_date=created_date,
            last_modified=modified_date,
            entry_count=5,
            total_amount=100.50,
            icon_color="#FF0000"
        )
        
        result = cashbook.to_dict()
        
        expected = {
            "id": "test-id",
            "name": "Test Cashbook",
            "description": "Test description",
            "category": "Personal",
            "created_date": "2023-01-01T12:00:00",
            "last_modified": "2023-01-02T12:00:00",
            "entry_count": 5,
            "total_amount": 100.50,
            "icon_color": "#FF0000"
        }
        
        assert result == expected
    
    def test_cashbook_from_dict(self):
        """Test creating cashbook from dictionary."""
        data = {
            "id": "test-id",
            "name": "Test Cashbook",
            "description": "Test description",
            "category": "Personal",
            "created_date": "2023-01-01T12:00:00",
            "last_modified": "2023-01-02T12:00:00",
            "entry_count": 5,
            "total_amount": 100.50,
            "icon_color": "#FF0000"
        }
        
        cashbook = Cashbook.from_dict(data)
        
        assert cashbook.id == "test-id"
        assert cashbook.name == "Test Cashbook"
        assert cashbook.description == "Test description"
        assert cashbook.category == "Personal"
        assert cashbook.created_date == datetime(2023, 1, 1, 12, 0, 0)
        assert cashbook.last_modified == datetime(2023, 1, 2, 12, 0, 0)
        assert cashbook.entry_count == 5
        assert cashbook.total_amount == 100.50
        assert cashbook.icon_color == "#FF0000"
    
    def test_cashbook_from_dict_minimal(self):
        """Test creating cashbook from dictionary with minimal data."""
        data = {
            "id": "test-id",
            "name": "Test",
            "created_date": "2023-01-01T12:00:00",
            "last_modified": "2023-01-01T12:00:00"
        }
        
        cashbook = Cashbook.from_dict(data)
        
        assert cashbook.id == "test-id"
        assert cashbook.name == "Test"
        assert cashbook.description == ""
        assert cashbook.category == ""
        assert cashbook.entry_count == 0
        assert cashbook.total_amount == 0.0
        assert cashbook.icon_color == "#3B82F6"
    
    def test_cashbook_serialization_roundtrip(self):
        """Test that serialization and deserialization preserve data."""
        original = Cashbook(
            id="test-id",
            name="Test Cashbook",
            description="Test description",
            category="Personal",
            entry_count=10,
            total_amount=250.75
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = Cashbook.from_dict(data)
        
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.category == original.category
        assert restored.entry_count == original.entry_count
        assert restored.total_amount == original.total_amount
        assert restored.icon_color == original.icon_color


class TestCashbookMetadata:
    """Test cases for the CashbookMetadata dataclass."""
    
    def test_metadata_creation_default(self):
        """Test creating metadata with default values."""
        metadata = CashbookMetadata()
        
        assert metadata.total_cashbooks == 0
        assert metadata.recent_activity == []
        assert metadata.categories == []
        assert metadata.last_backup is None
    
    def test_metadata_creation_with_values(self):
        """Test creating metadata with specific values."""
        backup_time = datetime(2023, 1, 1, 12, 0, 0)
        
        metadata = CashbookMetadata(
            total_cashbooks=5,
            recent_activity=["id1", "id2", "id3"],
            categories=["Personal", "Business"],
            last_backup=backup_time
        )
        
        assert metadata.total_cashbooks == 5
        assert metadata.recent_activity == ["id1", "id2", "id3"]
        assert metadata.categories == ["Personal", "Business"]
        assert metadata.last_backup == backup_time
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        backup_time = datetime(2023, 1, 1, 12, 0, 0)
        
        metadata = CashbookMetadata(
            total_cashbooks=3,
            recent_activity=["id1", "id2"],
            categories=["Personal"],
            last_backup=backup_time
        )
        
        result = metadata.to_dict()
        
        expected = {
            "total_cashbooks": 3,
            "recent_activity": ["id1", "id2"],
            "categories": ["Personal"],
            "last_backup": "2023-01-01T12:00:00"
        }
        
        assert result == expected
    
    def test_metadata_to_dict_no_backup(self):
        """Test converting metadata to dictionary with no backup time."""
        metadata = CashbookMetadata(
            total_cashbooks=2,
            recent_activity=["id1"],
            categories=["Personal"]
        )
        
        result = metadata.to_dict()
        
        expected = {
            "total_cashbooks": 2,
            "recent_activity": ["id1"],
            "categories": ["Personal"],
            "last_backup": None
        }
        
        assert result == expected
    
    def test_metadata_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            "total_cashbooks": 3,
            "recent_activity": ["id1", "id2"],
            "categories": ["Personal", "Business"],
            "last_backup": "2023-01-01T12:00:00"
        }
        
        metadata = CashbookMetadata.from_dict(data)
        
        assert metadata.total_cashbooks == 3
        assert metadata.recent_activity == ["id1", "id2"]
        assert metadata.categories == ["Personal", "Business"]
        assert metadata.last_backup == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_metadata_from_dict_minimal(self):
        """Test creating metadata from dictionary with minimal data."""
        data = {}
        
        metadata = CashbookMetadata.from_dict(data)
        
        assert metadata.total_cashbooks == 0
        assert metadata.recent_activity == []
        assert metadata.categories == []
        assert metadata.last_backup is None
    
    def test_metadata_serialization_roundtrip(self):
        """Test that metadata serialization and deserialization preserve data."""
        backup_time = datetime(2023, 1, 1, 12, 0, 0)
        
        original = CashbookMetadata(
            total_cashbooks=5,
            recent_activity=["id1", "id2", "id3"],
            categories=["Personal", "Business", "Travel"],
            last_backup=backup_time
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = CashbookMetadata.from_dict(data)
        
        assert restored.total_cashbooks == original.total_cashbooks
        assert restored.recent_activity == original.recent_activity
        assert restored.categories == original.categories
        assert restored.last_backup == original.last_backup


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_generate_cashbook_id(self):
        """Test that generate_cashbook_id creates unique IDs."""
        id1 = generate_cashbook_id()
        id2 = generate_cashbook_id()
        
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2
        assert len(id1) > 0
        assert len(id2) > 0
    
    def test_generate_cashbook_id_format(self):
        """Test that generated IDs are valid UUIDs."""
        import uuid
        
        cashbook_id = generate_cashbook_id()
        
        # Should be able to parse as UUID
        try:
            uuid.UUID(cashbook_id)
        except ValueError:
            pytest.fail(f"Generated ID '{cashbook_id}' is not a valid UUID")
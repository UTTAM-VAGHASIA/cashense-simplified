"""
Data models for the Cashbook Dashboard application.

This module contains the core data structures for managing cashbooks
and their metadata using Python dataclasses with validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid
import json


@dataclass
class Cashbook:
    """
    Represents a single cashbook with its metadata and statistics.
    
    Attributes:
        id: Unique identifier for the cashbook
        name: User-defined name for the cashbook
        description: Optional description of the cashbook's purpose
        category: Optional category for organizing cashbooks
        created_date: When the cashbook was created
        last_modified: When the cashbook was last updated
        entry_count: Number of expense entries in this cashbook
        total_amount: Sum of all expense amounts
        icon_color: Color code for visual differentiation
    """
    id: str
    name: str
    description: str = ""
    category: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    entry_count: int = 0
    total_amount: float = 0.0
    icon_color: str = "#3B82F6"  # Default blue color
    
    def __post_init__(self):
        """Validate cashbook data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Cashbook name cannot be empty")
        
        if len(self.name.strip()) > 100:
            raise ValueError("Cashbook name cannot exceed 100 characters")
        
        if self.entry_count < 0:
            raise ValueError("Entry count cannot be negative")
        
        # Ensure name is stripped of whitespace
        self.name = self.name.strip()
    
    def to_dict(self) -> dict:
        """Convert cashbook to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "created_date": self.created_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "entry_count": self.entry_count,
            "total_amount": self.total_amount,
            "icon_color": self.icon_color
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Cashbook':
        """Create cashbook from dictionary (JSON deserialization)."""
        # Parse datetime strings back to datetime objects
        created_date = datetime.fromisoformat(data["created_date"])
        last_modified = datetime.fromisoformat(data["last_modified"])
        
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            created_date=created_date,
            last_modified=last_modified,
            entry_count=data.get("entry_count", 0),
            total_amount=data.get("total_amount", 0.0),
            icon_color=data.get("icon_color", "#3B82F6")
        )


@dataclass
class CashbookMetadata:
    """
    Metadata about the collection of cashbooks.
    
    Attributes:
        total_cashbooks: Total number of cashbooks
        recent_activity: List of recent cashbook IDs (most recent first)
        categories: List of unique categories used
        last_backup: When the data was last backed up
    """
    total_cashbooks: int = 0
    recent_activity: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    last_backup: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert metadata to dictionary for JSON serialization."""
        return {
            "total_cashbooks": self.total_cashbooks,
            "recent_activity": self.recent_activity,
            "categories": self.categories,
            "last_backup": self.last_backup.isoformat() if self.last_backup else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CashbookMetadata':
        """Create metadata from dictionary (JSON deserialization)."""
        last_backup = None
        if data.get("last_backup"):
            last_backup = datetime.fromisoformat(data["last_backup"])
        
        return cls(
            total_cashbooks=data.get("total_cashbooks", 0),
            recent_activity=data.get("recent_activity", []),
            categories=data.get("categories", []),
            last_backup=last_backup
        )


def generate_cashbook_id() -> str:
    """Generate a unique ID for a new cashbook."""
    return str(uuid.uuid4())
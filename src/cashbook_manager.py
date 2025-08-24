"""
Cashbook Manager for handling CRUD operations and data persistence.

This module provides the CashbookManager class that handles all operations
related to cashbook management including creation, reading, updating, deletion,
and JSON file persistence.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from .models import Cashbook, CashbookMetadata, generate_cashbook_id


class CashbookManager:
    """
    Manages cashbook data with JSON file persistence.
    
    Handles CRUD operations for cashbooks and maintains metadata
    about the collection. Data is stored in JSON files in the
    user's application data directory.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the cashbook manager.
        
        Args:
            data_dir: Optional custom directory for data storage.
                     If None, uses default application data directory.
        """
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # Use user's application data directory
            home = Path.home()
            self.data_dir = home / ".cashense"
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.cashbooks_file = self.data_dir / "cashbooks.json"
        self.metadata_file = self.data_dir / "metadata.json"
        
        # In-memory cache
        self._cashbooks: Dict[str, Cashbook] = {}
        self._metadata: CashbookMetadata = CashbookMetadata()
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load cashbooks and metadata from JSON files."""
        try:
            # Load cashbooks
            if self.cashbooks_file.exists():
                with open(self.cashbooks_file, 'r', encoding='utf-8') as f:
                    cashbooks_data = json.load(f)
                    self._cashbooks = {
                        cashbook_id: Cashbook.from_dict(data)
                        for cashbook_id, data in cashbooks_data.items()
                    }
            
            # Load metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata_data = json.load(f)
                    self._metadata = CashbookMetadata.from_dict(metadata_data)
            
            # Update metadata if it's out of sync
            self._update_metadata()
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Handle corrupted data by creating backup and starting fresh
            self._handle_corrupted_data(e)
    
    def _save_data(self) -> None:
        """Save cashbooks and metadata to JSON files."""
        try:
            # Save cashbooks
            cashbooks_data = {
                cashbook_id: cashbook.to_dict()
                for cashbook_id, cashbook in self._cashbooks.items()
            }
            
            with open(self.cashbooks_file, 'w', encoding='utf-8') as f:
                json.dump(cashbooks_data, f, indent=2, ensure_ascii=False)
            
            # Save metadata
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._metadata.to_dict(), f, indent=2, ensure_ascii=False)
                
        except (OSError, IOError) as e:
            raise RuntimeError(f"Failed to save cashbook data: {e}")
    
    def _handle_corrupted_data(self, error: Exception) -> None:
        """Handle corrupted data files by creating backups and starting fresh."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create backup of corrupted files
        if self.cashbooks_file.exists():
            backup_file = self.data_dir / f"cashbooks_corrupted_{timestamp}.json"
            self.cashbooks_file.rename(backup_file)
        
        if self.metadata_file.exists():
            backup_file = self.data_dir / f"metadata_corrupted_{timestamp}.json"
            self.metadata_file.rename(backup_file)
        
        # Start with fresh data
        self._cashbooks = {}
        self._metadata = CashbookMetadata()
        
        print(f"Warning: Corrupted data detected ({error}). "
              f"Backup created with timestamp {timestamp}")
    
    def _update_metadata(self) -> None:
        """Update metadata based on current cashbooks."""
        self._metadata.total_cashbooks = len(self._cashbooks)
        
        # Update categories list
        categories = set()
        for cashbook in self._cashbooks.values():
            if cashbook.category:
                categories.add(cashbook.category)
        self._metadata.categories = sorted(list(categories))
        
        # Ensure recent activity list is valid
        valid_ids = set(self._cashbooks.keys())
        self._metadata.recent_activity = [
            cashbook_id for cashbook_id in self._metadata.recent_activity
            if cashbook_id in valid_ids
        ]
    
    def create_cashbook(self, name: str, description: str = "", category: str = "") -> Cashbook:
        """
        Create a new cashbook.
        
        Args:
            name: Name for the cashbook (required)
            description: Optional description
            category: Optional category
            
        Returns:
            The created Cashbook instance
            
        Raises:
            ValueError: If name is invalid
            RuntimeError: If save operation fails
        """
        # Generate unique ID
        cashbook_id = generate_cashbook_id()
        
        # Create cashbook (validation happens in __post_init__)
        cashbook = Cashbook(
            id=cashbook_id,
            name=name,
            description=description,
            category=category
        )
        
        # Add to cache
        self._cashbooks[cashbook_id] = cashbook
        
        # Update recent activity
        if cashbook_id in self._metadata.recent_activity:
            self._metadata.recent_activity.remove(cashbook_id)
        self._metadata.recent_activity.insert(0, cashbook_id)
        
        # Keep only last 10 in recent activity
        self._metadata.recent_activity = self._metadata.recent_activity[:10]
        
        # Update metadata and save
        self._update_metadata()
        self._save_data()
        
        return cashbook
    
    def get_recent_cashbooks(self, limit: int = 4) -> List[Cashbook]:
        """
        Get the most recently accessed cashbooks.
        
        Args:
            limit: Maximum number of cashbooks to return
            
        Returns:
            List of recent cashbooks, ordered by most recent first
        """
        recent_cashbooks = []
        
        for cashbook_id in self._metadata.recent_activity[:limit]:
            if cashbook_id in self._cashbooks:
                recent_cashbooks.append(self._cashbooks[cashbook_id])
        
        return recent_cashbooks
    
    def get_all_cashbooks(self) -> List[Cashbook]:
        """
        Get all cashbooks sorted by last modified date (newest first).
        
        Returns:
            List of all cashbooks
        """
        return sorted(
            self._cashbooks.values(),
            key=lambda cb: cb.last_modified,
            reverse=True
        )
    
    def get_cashbook(self, cashbook_id: str) -> Optional[Cashbook]:
        """
        Get a specific cashbook by ID.
        
        Args:
            cashbook_id: The cashbook ID to retrieve
            
        Returns:
            The cashbook if found, None otherwise
        """
        return self._cashbooks.get(cashbook_id)
    
    def update_cashbook(self, cashbook_id: str, **kwargs) -> bool:
        """
        Update an existing cashbook.
        
        Args:
            cashbook_id: ID of the cashbook to update
            **kwargs: Fields to update (name, description, category, etc.)
            
        Returns:
            True if updated successfully, False if cashbook not found
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If save operation fails
        """
        if cashbook_id not in self._cashbooks:
            return False
        
        cashbook = self._cashbooks[cashbook_id]
        
        # Update fields
        for field_name, value in kwargs.items():
            if hasattr(cashbook, field_name):
                setattr(cashbook, field_name, value)
        
        # Update last modified time
        cashbook.last_modified = datetime.now()
        
        # Validate updated cashbook
        cashbook.__post_init__()
        
        # Update recent activity
        if cashbook_id in self._metadata.recent_activity:
            self._metadata.recent_activity.remove(cashbook_id)
        self._metadata.recent_activity.insert(0, cashbook_id)
        
        # Update metadata and save
        self._update_metadata()
        self._save_data()
        
        return True
    
    def delete_cashbook(self, cashbook_id: str) -> bool:
        """
        Delete a cashbook.
        
        Args:
            cashbook_id: ID of the cashbook to delete
            
        Returns:
            True if deleted successfully, False if cashbook not found
            
        Raises:
            RuntimeError: If save operation fails
        """
        if cashbook_id not in self._cashbooks:
            return False
        
        # Remove from cache
        del self._cashbooks[cashbook_id]
        
        # Remove from recent activity
        if cashbook_id in self._metadata.recent_activity:
            self._metadata.recent_activity.remove(cashbook_id)
        
        # Update metadata and save
        self._update_metadata()
        self._save_data()
        
        return True
    
    def get_cashbook_stats(self, cashbook_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific cashbook.
        
        Args:
            cashbook_id: ID of the cashbook
            
        Returns:
            Dictionary with statistics or None if cashbook not found
        """
        cashbook = self.get_cashbook(cashbook_id)
        if not cashbook:
            return None
        
        return {
            "id": cashbook.id,
            "name": cashbook.name,
            "entry_count": cashbook.entry_count,
            "total_amount": cashbook.total_amount,
            "created_date": cashbook.created_date,
            "last_modified": cashbook.last_modified,
            "category": cashbook.category
        }
    
    def get_metadata(self) -> CashbookMetadata:
        """
        Get current metadata.
        
        Returns:
            Current CashbookMetadata instance
        """
        return self._metadata
    
    def backup_data(self) -> str:
        """
        Create a backup of all cashbook data.
        
        Returns:
            Path to the backup file
            
        Raises:
            RuntimeError: If backup creation fails
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.data_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_file = backup_dir / f"cashbooks_backup_{timestamp}.json"
        
        try:
            # Create comprehensive backup
            backup_data = {
                "cashbooks": {
                    cashbook_id: cashbook.to_dict()
                    for cashbook_id, cashbook in self._cashbooks.items()
                },
                "metadata": self._metadata.to_dict(),
                "backup_timestamp": datetime.now().isoformat()
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Update metadata
            self._metadata.last_backup = datetime.now()
            self._save_data()
            
            return str(backup_file)
            
        except (OSError, IOError) as e:
            raise RuntimeError(f"Failed to create backup: {e}")
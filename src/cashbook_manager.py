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
try:
    from models import Cashbook, CashbookMetadata, generate_cashbook_id
except ImportError:
    from .models import Cashbook, CashbookMetadata, generate_cashbook_id


class CashbookError(Exception):
    """Base exception for cashbook-related errors."""
    pass


class FileOperationError(CashbookError):
    """Exception raised for file I/O operation errors."""
    pass


class DataCorruptionError(CashbookError):
    """Exception raised when data corruption is detected."""
    pass


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
        """Load cashbooks and metadata from JSON files with comprehensive error handling."""
        try:
            # Load cashbooks with error recovery
            if self.cashbooks_file.exists():
                try:
                    with open(self.cashbooks_file, 'r', encoding='utf-8') as f:
                        cashbooks_data = json.load(f)
                        self._cashbooks = {}
                        
                        # Load each cashbook individually to handle partial corruption
                        for cashbook_id, data in cashbooks_data.items():
                            try:
                                cashbook = Cashbook.from_dict(data)
                                self._cashbooks[cashbook_id] = cashbook
                            except (KeyError, ValueError, TypeError) as e:
                                print(f"Warning: Skipping corrupted cashbook {cashbook_id}: {e}")
                                continue
                                
                except (OSError, IOError) as e:
                    raise FileOperationError(f"Cannot read cashbooks file: {e}")
                except json.JSONDecodeError as e:
                    raise DataCorruptionError(f"Cashbooks file is corrupted: {e}")
            
            # Load metadata with error recovery
            if self.metadata_file.exists():
                try:
                    with open(self.metadata_file, 'r', encoding='utf-8') as f:
                        metadata_data = json.load(f)
                        self._metadata = CashbookMetadata.from_dict(metadata_data)
                except (OSError, IOError) as e:
                    print(f"Warning: Cannot read metadata file: {e}")
                    self._metadata = CashbookMetadata()
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    print(f"Warning: Metadata file corrupted, using defaults: {e}")
                    self._metadata = CashbookMetadata()
            
            # Update metadata if it's out of sync
            self._update_metadata()
            
        except (DataCorruptionError, FileOperationError) as e:
            # Handle serious errors by creating backup and starting fresh
            self._handle_corrupted_data(e)
        except Exception as e:
            # Catch any unexpected errors
            print(f"Unexpected error loading data: {e}")
            self._handle_corrupted_data(e)
    
    def _save_data(self) -> None:
        """Save cashbooks and metadata to JSON files with atomic operations."""
        import tempfile
        import shutil
        
        try:
            # Create temporary files for atomic writes
            cashbooks_temp = None
            metadata_temp = None
            
            try:
                # Save cashbooks atomically
                cashbooks_data = {
                    cashbook_id: cashbook.to_dict()
                    for cashbook_id, cashbook in self._cashbooks.items()
                }
                
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    encoding='utf-8', 
                    dir=self.data_dir, 
                    delete=False,
                    suffix='.tmp'
                ) as f:
                    json.dump(cashbooks_data, f, indent=2, ensure_ascii=False)
                    cashbooks_temp = f.name
                
                # Save metadata atomically
                with tempfile.NamedTemporaryFile(
                    mode='w', 
                    encoding='utf-8', 
                    dir=self.data_dir, 
                    delete=False,
                    suffix='.tmp'
                ) as f:
                    json.dump(self._metadata.to_dict(), f, indent=2, ensure_ascii=False)
                    metadata_temp = f.name
                
                # Atomic moves (replace existing files)
                shutil.move(cashbooks_temp, self.cashbooks_file)
                shutil.move(metadata_temp, self.metadata_file)
                
            except Exception as e:
                # Clean up temporary files on error
                if cashbooks_temp and os.path.exists(cashbooks_temp):
                    os.unlink(cashbooks_temp)
                if metadata_temp and os.path.exists(metadata_temp):
                    os.unlink(metadata_temp)
                raise
                
        except (OSError, IOError) as e:
            raise FileOperationError(f"Failed to save cashbook data: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error saving data: {e}")
    
    def _handle_corrupted_data(self, error: Exception) -> None:
        """Handle corrupted data files by creating backups and starting fresh."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_created = False
        
        try:
            # Ensure backup directory exists
            backup_dir = self.data_dir / "corrupted_backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Create backup of corrupted files
            if self.cashbooks_file.exists():
                backup_file = backup_dir / f"cashbooks_corrupted_{timestamp}.json"
                try:
                    import shutil
                    shutil.copy2(self.cashbooks_file, backup_file)
                    backup_created = True
                except (OSError, IOError) as e:
                    print(f"Warning: Could not create backup of cashbooks file: {e}")
            
            if self.metadata_file.exists():
                backup_file = backup_dir / f"metadata_corrupted_{timestamp}.json"
                try:
                    import shutil
                    shutil.copy2(self.metadata_file, backup_file)
                    backup_created = True
                except (OSError, IOError) as e:
                    print(f"Warning: Could not create backup of metadata file: {e}")
            
            # Try to recover partial data before starting fresh
            recovered_cashbooks = self._attempt_data_recovery()
            
            # Start with fresh data (keeping any recovered cashbooks)
            self._cashbooks = recovered_cashbooks
            self._metadata = CashbookMetadata()
            self._update_metadata()
            
            # Save the recovered/fresh data
            try:
                self._save_data()
            except Exception as save_error:
                print(f"Warning: Could not save recovered data: {save_error}")
            
            recovery_msg = f"Data corruption detected ({error}). "
            if backup_created:
                recovery_msg += f"Backup created in corrupted_backups/ with timestamp {timestamp}. "
            if recovered_cashbooks:
                recovery_msg += f"Recovered {len(recovered_cashbooks)} cashbooks. "
            else:
                recovery_msg += "Starting with fresh data. "
            
            print(f"Warning: {recovery_msg}")
            
        except Exception as recovery_error:
            print(f"Critical error during data recovery: {recovery_error}")
            # Last resort: start completely fresh
            self._cashbooks = {}
            self._metadata = CashbookMetadata()
    
    def _attempt_data_recovery(self) -> Dict[str, Cashbook]:
        """Attempt to recover partial data from corrupted files."""
        recovered_cashbooks = {}
        
        # Try to recover from cashbooks file
        if self.cashbooks_file.exists():
            try:
                with open(self.cashbooks_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Try to parse as JSON
                try:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        for cashbook_id, cashbook_data in data.items():
                            try:
                                cashbook = Cashbook.from_dict(cashbook_data)
                                recovered_cashbooks[cashbook_id] = cashbook
                            except Exception:
                                continue  # Skip corrupted individual cashbooks
                except json.JSONDecodeError:
                    # Try line-by-line recovery for partially corrupted JSON
                    lines = content.split('\n')
                    for line in lines:
                        if '"id":' in line and '"name":' in line:
                            # Try to extract cashbook data from individual lines
                            try:
                                # This is a simplified recovery - in practice, you might
                                # implement more sophisticated JSON repair techniques
                                pass
                            except Exception:
                                continue
                                
            except (OSError, IOError):
                pass  # File not readable
        
        return recovered_cashbooks
    
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
        
        try:
            self._save_data()
        except FileOperationError:
            # Remove the cashbook from cache if save failed
            del self._cashbooks[cashbook_id]
            if cashbook_id in self._metadata.recent_activity:
                self._metadata.recent_activity.remove(cashbook_id)
            self._update_metadata()
            raise
        except Exception as e:
            # Remove the cashbook from cache if save failed
            del self._cashbooks[cashbook_id]
            if cashbook_id in self._metadata.recent_activity:
                self._metadata.recent_activity.remove(cashbook_id)
            self._update_metadata()
            raise FileOperationError(f"Failed to save cashbook: {e}")
        
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
        
        try:
            self._save_data()
        except FileOperationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Failed to save cashbook updates: {e}")
        
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
        
        try:
            self._save_data()
        except FileOperationError:
            raise
        except Exception as e:
            raise FileOperationError(f"Failed to save after deleting cashbook: {e}")
        
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
    
    def get_error_recovery_info(self) -> Dict[str, Any]:
        """Get information about data recovery and error status."""
        backup_dir = self.data_dir / "corrupted_backups"
        recovery_info = {
            "data_directory": str(self.data_dir),
            "has_backups": backup_dir.exists() and any(backup_dir.iterdir()),
            "backup_directory": str(backup_dir) if backup_dir.exists() else None,
            "last_backup": self._metadata.last_backup.isoformat() if self._metadata.last_backup else None,
            "total_cashbooks": len(self._cashbooks),
            "data_files_exist": {
                "cashbooks": self.cashbooks_file.exists(),
                "metadata": self.metadata_file.exists()
            }
        }
        
        if backup_dir.exists():
            try:
                backups = list(backup_dir.glob("*_corrupted_*.json"))
                recovery_info["available_backups"] = [
                    {
                        "filename": backup.name,
                        "created": datetime.fromtimestamp(backup.stat().st_mtime).isoformat(),
                        "size": backup.stat().st_size
                    }
                    for backup in sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True)
                ]
            except (OSError, IOError):
                recovery_info["available_backups"] = []
        else:
            recovery_info["available_backups"] = []
        
        return recovery_info
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate the integrity of loaded data and return status report."""
        integrity_report = {
            "is_valid": True,
            "issues": [],
            "cashbook_count": len(self._cashbooks),
            "metadata_sync": True
        }
        
        # Check if metadata is in sync with actual cashbooks
        actual_count = len(self._cashbooks)
        if self._metadata.total_cashbooks != actual_count:
            integrity_report["is_valid"] = False
            integrity_report["metadata_sync"] = False
            integrity_report["issues"].append(
                f"Metadata count ({self._metadata.total_cashbooks}) doesn't match actual count ({actual_count})"
            )
        
        # Check if recent activity references valid cashbooks
        invalid_recent = [
            cb_id for cb_id in self._metadata.recent_activity 
            if cb_id not in self._cashbooks
        ]
        if invalid_recent:
            integrity_report["is_valid"] = False
            integrity_report["issues"].append(
                f"Recent activity contains {len(invalid_recent)} invalid cashbook references"
            )
        
        # Validate individual cashbooks
        invalid_cashbooks = []
        for cashbook_id, cashbook in self._cashbooks.items():
            try:
                # Re-validate the cashbook
                cashbook.__post_init__()
            except ValueError as e:
                invalid_cashbooks.append((cashbook_id, str(e)))
        
        if invalid_cashbooks:
            integrity_report["is_valid"] = False
            integrity_report["issues"].append(
                f"Found {len(invalid_cashbooks)} invalid cashbooks"
            )
            integrity_report["invalid_cashbooks"] = invalid_cashbooks
        
        return integrity_report
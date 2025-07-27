"""
Document Type Manager for OCR Invoice Parser
Handles document type CRUD operations and business logic
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class DocumentTypeManager(QObject):
    """
    Manages document types in the database.
    Provides CRUD operations for document types.
    """
    
    # Signals
    document_type_added = pyqtSignal(str)  # Emits document type name
    document_type_updated = pyqtSignal(str)  # Emits document type name
    document_type_deleted = pyqtSignal(str)  # Emits document type name
    document_types_changed = pyqtSignal()  # Emitted when any change occurs
    
    def __init__(self, database_manager):
        super().__init__()
        self.database_manager = database_manager
        self._ensure_table_exists()
    
    def _ensure_table_exists(self) -> None:
        """Ensure the document_types table exists."""
        try:
            # Create the table if it doesn't exist
            self.database_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS document_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    is_default BOOLEAN DEFAULT 0,
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if table is empty and insert default values
            cursor = self.database_manager.execute_query("SELECT COUNT(*) FROM document_types")
            if cursor.fetchone()[0] == 0:
                self._insert_default_document_types()
        except sqlite3.Error as e:
            logger.error(f"Error ensuring document_types table exists: {e}")
            raise
    
    def _insert_default_document_types(self) -> None:
        """Insert default document types if table is empty."""
        default_types = [
            ('Invoice', 'Standard invoice documents', 1, 1),
            ('Credit Card', 'Credit card statements', 0, 2),
            ('Receipt', 'General receipts', 0, 3),
            ('Other', 'Other document types', 0, 4)
        ]
        
        self.database_manager.execute_many("""
            INSERT INTO document_types (name, description, is_default, sort_order) 
            VALUES (?, ?, ?, ?)
        """, default_types)
    
    def get_all_document_types(self) -> List[Dict[str, any]]:
        """
        Get all document types ordered by sort_order.
        
        Returns:
            List of document type dictionaries with keys: id, name, description, is_default, sort_order
        """
        try:
            cursor = self.database_manager.execute_query("""
                SELECT id, name, description, is_default, sort_order, created_at, updated_at
                FROM document_types
                ORDER BY sort_order, name
            """)
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting all document types: {e}")
            return []
    
    def get_document_type_names(self) -> List[str]:
        """
        Get list of document type names ordered by sort_order.
        
        Returns:
            List of document type names
        """
        try:
            cursor = self.database_manager.execute_query("""
                SELECT name FROM document_types
                ORDER BY sort_order, name
            """)
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting document type names: {e}")
            return []
    
    def get_default_document_type(self) -> Optional[str]:
        """
        Get the default document type name.
        
        Returns:
            Default document type name or None if not found
        """
        try:
            cursor = self.database_manager.execute_query("""
                SELECT name FROM document_types
                WHERE is_default = 1
                ORDER BY sort_order, name
                LIMIT 1
            """)
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"Error getting default document type: {e}")
            return None
    
    def add_document_type(self, name: str, description: str = "", is_default: bool = False) -> bool:
        """
        Add a new document type.
        
        Args:
            name: Document type name
            description: Optional description
            is_default: Whether this should be the default type
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # If this is being set as default, unset other defaults first
            if is_default:
                self.database_manager.execute_query("""
                    UPDATE document_types SET is_default = 0
                """)
            
            # Get the next sort order
            cursor = self.database_manager.execute_query("""
                SELECT COALESCE(MAX(sort_order), 0) + 1 FROM document_types
            """)
            next_sort_order = cursor.fetchone()[0]
            
            # Insert the new document type
            self.database_manager.execute_query("""
                INSERT INTO document_types (name, description, is_default, sort_order)
                VALUES (?, ?, ?, ?)
            """, (name, description, 1 if is_default else 0, next_sort_order))
            
            # Emit signals
            self.document_type_added.emit(name)
            self.document_types_changed.emit()
            
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding document type: {e}")
            return False
    
    def update_document_type(self, old_name: str, new_name: str, description: str = "", is_default: bool = False) -> bool:
        """
        Update an existing document type.
        
        Args:
            old_name: Current document type name
            new_name: New document type name
            description: Optional description
            is_default: Whether this should be the default type
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Check if the current type is the default
            cursor = self.database_manager.execute_query("""
                SELECT is_default FROM document_types WHERE name = ?
            """, (old_name,))
            result = cursor.fetchone()
            if not result:
                return False
            
            was_default = result[0]
            
            # If this is being set as default, unset other defaults first
            if is_default:
                self.database_manager.execute_query("""
                    UPDATE document_types SET is_default = 0
                """)
            
            # Update the document type
            self.database_manager.execute_query("""
                UPDATE document_types 
                SET name = ?, description = ?, is_default = ?, updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            """, (new_name, description, 1 if is_default else 0, old_name))
            
            # Check if any rows were affected
            cursor = self.database_manager.execute_query("SELECT changes()")
            if cursor.fetchone()[0] > 0:
                # If we removed the default and didn't set a new one, set the first remaining type as default
                if was_default and not is_default:
                    cursor = self.database_manager.execute_query("""
                        SELECT name FROM document_types WHERE name != ? ORDER BY sort_order, name LIMIT 1
                    """, (new_name,))
                    result = cursor.fetchone()
                    if result:
                        self.database_manager.execute_query("""
                            UPDATE document_types SET is_default = 1 WHERE name = ?
                        """, (result[0],))
                
                # Emit signals
                self.document_type_updated.emit(new_name)
                self.document_types_changed.emit()
                return True
            return False
        except sqlite3.Error as e:
            logger.error(f"Error updating document type: {e}")
            return False
    
    def delete_document_type(self, name: str) -> bool:
        """
        Delete a document type.
        
        Args:
            name: Document type name to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Check if this is the default type
            cursor = self.database_manager.execute_query("""
                SELECT is_default FROM document_types WHERE name = ?
            """, (name,))
            result = cursor.fetchone()
            if not result:
                return False
            
            is_default = result[0]
            
            # Delete the document type
            self.database_manager.execute_query("""
                DELETE FROM document_types WHERE name = ?
            """, (name,))
            
            # Check if any rows were affected
            cursor = self.database_manager.execute_query("SELECT changes()")
            if cursor.fetchone()[0] > 0:
                # If we deleted the default type, set the first remaining type as default
                if is_default:
                    cursor = self.database_manager.execute_query("""
                        SELECT name FROM document_types ORDER BY sort_order, name LIMIT 1
                    """)
                    result = cursor.fetchone()
                    if result:
                        self.database_manager.execute_query("""
                            UPDATE document_types SET is_default = 1 WHERE name = ?
                        """, (result[0],))
                
                # Emit signals
                self.document_type_deleted.emit(name)
                self.document_types_changed.emit()
                return True
            return False
        except sqlite3.Error as e:
            logger.error(f"Error deleting document type: {e}")
            return False
    
    def set_default_document_type(self, name: str) -> bool:
        """
        Set a document type as the default.
        
        Args:
            name: Document type name to set as default
            
        Returns:
            True if set successfully, False otherwise
        """
        try:
            # Unset all current defaults
            self.database_manager.execute_query("""
                UPDATE document_types SET is_default = 0
            """)
            
            # Set the new default
            self.database_manager.execute_query("""
                UPDATE document_types SET is_default = 1 WHERE name = ?
            """, (name,))
            
            # Check if any rows were affected
            cursor = self.database_manager.execute_query("SELECT changes()")
            if cursor.fetchone()[0] > 0:
                # Emit signals
                self.document_type_updated.emit(name)
                self.document_types_changed.emit()
                return True
            return False
        except sqlite3.Error as e:
            logger.error(f"Error setting default document type: {e}")
            return False
    
    def reorder_document_types(self, name_order: List[str]) -> bool:
        """
        Reorder document types based on the provided list.
        
        Args:
            name_order: List of document type names in desired order
            
        Returns:
            True if reordered successfully, False otherwise
        """
        try:
            # Update sort order for each document type
            for index, name in enumerate(name_order, 1):
                self.database_manager.execute_query("""
                    UPDATE document_types SET sort_order = ? WHERE name = ?
                """, (index, name))
            
            # Emit signal
            self.document_types_changed.emit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error reordering document types: {e}")
            return False 
"""
PDFMetadataManager: Handles CRUD operations and validation for invoice metadata in the OCR Invoice Parser.
"""
from typing import List, Optional, Dict, Any
from .database_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class PDFMetadataManager:
    """
    Manages CRUD operations and validation for invoice metadata.
    """
    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize PDFMetadataManager with a DatabaseManager instance.
        """
        self.db_manager = db_manager

    def create_metadata(self, file_path: str, data: Dict[str, Any]) -> int:
        """
        Create a new invoice metadata record.
        Args:
            file_path: Path to the PDF file.
            data: Dictionary of metadata fields.
        Returns:
            The ID of the created metadata record.
        Raises:
            ValueError: If the file_path is invalid or already exists.
        """
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty.")
        if self.get_metadata_by_file_path(file_path):
            raise ValueError(f"Metadata for '{file_path}' already exists.")
        try:
            fields = ["file_path"] + list(data.keys())
            placeholders = ["?"] * len(fields)
            values = [file_path] + list(data.values())
            cursor = self.db_manager.execute_query(
                f"INSERT INTO invoice_metadata ({', '.join(fields)}) VALUES ({', '.join(placeholders)})",
                tuple(values)
            )
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create metadata: {e}")
            raise

    def get_metadata_by_id(self, metadata_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve invoice metadata by its ID.
        Args:
            metadata_id: The metadata record ID.
        Returns:
            Metadata as a dict, or None if not found.
        """
        try:
            cursor = self.db_manager.execute_query(
                "SELECT * FROM invoice_metadata WHERE id = ?",
                (metadata_id,)
            )
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Failed to get metadata by id: {e}")
            raise

    def get_metadata_by_file_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve invoice metadata by file path.
        Args:
            file_path: The PDF file path.
        Returns:
            Metadata as a dict, or None if not found.
        """
        try:
            cursor = self.db_manager.execute_query(
                "SELECT * FROM invoice_metadata WHERE file_path = ?",
                (file_path.strip(),)
            )
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Failed to get metadata by file path: {e}")
            raise

    def list_metadata(self) -> List[Dict[str, Any]]:
        """
        List all invoice metadata records.
        Returns:
            List of metadata dicts.
        """
        try:
            cursor = self.db_manager.execute_query(
                "SELECT * FROM invoice_metadata ORDER BY extracted_at DESC"
            )
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to list metadata: {e}")
            raise

    def update_metadata(self, metadata_id: int, data: Dict[str, Any]) -> None:
        """
        Update an invoice metadata record.
        Args:
            metadata_id: The metadata record ID.
            data: Dictionary of fields to update.
        Raises:
            ValueError: If no update fields are provided or record does not exist.
        """
        if not self.get_metadata_by_id(metadata_id):
            raise ValueError(f"Metadata with id {metadata_id} does not exist.")
        if not data:
            raise ValueError("No update fields provided.")
        fields = [f"{k} = ?" for k in data.keys()]
        values = list(data.values())
        values.append(metadata_id)
        try:
            self.db_manager.execute_query(
                f"UPDATE invoice_metadata SET {', '.join(fields)} WHERE id = ?",
                tuple(values)
            )
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            raise

    def delete_metadata(self, metadata_id: int) -> None:
        """
        Delete an invoice metadata record by its ID.
        Args:
            metadata_id: The metadata record ID.
        Raises:
            ValueError: If the record does not exist.
        """
        if not self.get_metadata_by_id(metadata_id):
            raise ValueError(f"Metadata with id {metadata_id} does not exist.")
        try:
            self.db_manager.execute_query(
                "DELETE FROM invoice_metadata WHERE id = ?",
                (metadata_id,)
            )
        except Exception as e:
            logger.error(f"Failed to delete metadata: {e}")
            raise 
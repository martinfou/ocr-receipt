"""
CategoryManager: Handles CRUD operations and validation for categories in the OCR Invoice Parser.
"""
from typing import List, Optional, Dict, Any
from .database_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class CategoryManager:
    """
    Manages category CRUD operations and validation.
    """
    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize CategoryManager with a DatabaseManager instance.
        """
        self.db_manager = db_manager

    def create_category(self, name: str, description: Optional[str] = None, category_code: Optional[str] = None) -> int:
        """
        Create a new category.
        Args:
            name: Category name.
            description: Optional category description.
            category_code: Optional category code.
        Returns:
            The ID of the created category.
        Raises:
            ValueError: If the category name is invalid or already exists.
        """
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty.")
        if self.get_category_by_name(name):
            raise ValueError(f"Category '{name}' already exists.")
        try:
            cursor = self.db_manager.execute_query(
                """
                INSERT INTO categories (name, description, category_code)
                VALUES (?, ?, ?)
                """,
                (name.strip(), description, category_code)
            )
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create category: {e}")
            raise

    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a category by its ID.
        Args:
            category_id: The category ID.
        Returns:
            Category as a dict, or None if not found.
        """
        try:
            cursor = self.db_manager.execute_query(
                "SELECT id, name, description, category_code FROM categories WHERE id = ?",
                (category_id,)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "description": row[2], "category_code": row[3]}
            return None
        except Exception as e:
            logger.error(f"Failed to get category by id: {e}")
            raise

    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a category by its name.
        Args:
            name: The category name.
        Returns:
            Category as a dict, or None if not found.
        """
        try:
            cursor = self.db_manager.execute_query(
                "SELECT id, name, description, category_code FROM categories WHERE name = ?",
                (name.strip(),)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "description": row[2], "category_code": row[3]}
            return None
        except Exception as e:
            logger.error(f"Failed to get category by name: {e}")
            raise

    def list_categories(self) -> List[Dict[str, Any]]:
        """
        List all categories.
        Returns:
            List of category dicts.
        """
        try:
            cursor = self.db_manager.execute_query(
                "SELECT id, name, description, category_code FROM categories ORDER BY name ASC"
            )
            return [
                {"id": row[0], "name": row[1], "description": row[2], "category_code": row[3]}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            logger.error(f"Failed to list categories: {e}")
            raise

    def update_category(self, category_id: int, name: Optional[str] = None, description: Optional[str] = None, category_code: Optional[str] = None) -> None:
        """
        Update a category's name, description, and/or code.
        Args:
            category_id: The category ID.
            name: New name (optional).
            description: New description (optional).
            category_code: New category code (optional).
        Raises:
            ValueError: If no update fields are provided or category does not exist.
        """
        if name is not None and not name.strip():
            raise ValueError("Category name cannot be empty.")
        if not self.get_category_by_id(category_id):
            raise ValueError(f"Category with id {category_id} does not exist.")
        fields = []
        values = []
        if name is not None:
            fields.append("name = ?")
            values.append(name.strip())
        if description is not None:
            fields.append("description = ?")
            values.append(description)
        if category_code is not None:
            fields.append("category_code = ?")
            values.append(category_code)
        if not fields:
            raise ValueError("No update fields provided.")
        values.append(category_id)
        try:
            self.db_manager.execute_query(
                f"UPDATE categories SET {', '.join(fields)} WHERE id = ?",
                tuple(values)
            )
        except Exception as e:
            logger.error(f"Failed to update category: {e}")
            raise

    def delete_category(self, category_id: int) -> None:
        """
        Delete a category by its ID.
        Args:
            category_id: The category ID.
        Raises:
            ValueError: If the category does not exist.
        """
        if not self.get_category_by_id(category_id):
            raise ValueError(f"Category with id {category_id} does not exist.")
        try:
            self.db_manager.execute_query(
                "DELETE FROM categories WHERE id = ?",
                (category_id,)
            )
        except Exception as e:
            logger.error(f"Failed to delete category: {e}")
            raise 
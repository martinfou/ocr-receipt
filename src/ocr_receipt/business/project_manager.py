"""
ProjectManager: Handles CRUD operations and validation for projects in the OCR Invoice Parser.
"""
from typing import List, Optional, Dict, Any
from .database_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class ProjectManager:
    """
    Manages project CRUD operations and validation.
    """
    def __init__(self, db_manager: DatabaseManager) -> None:
        """
        Initialize ProjectManager with a DatabaseManager instance.
        """
        self.db_manager = db_manager

    def create_project(self, name: str, description: Optional[str] = None) -> int:
        """
        Create a new project.
        Args:
            name: Project name.
            description: Optional project description.
        Returns:
            The ID of the created project.
        Raises:
            ValueError: If the project name is invalid or already exists.
        """
        if not name or not name.strip():
            raise ValueError("Project name cannot be empty.")
        if self.get_project_by_name(name):
            raise ValueError(f"Project '{name}' already exists.")
        try:
            cursor = self.db_manager.execute_query(
                """
                INSERT INTO projects (name, description)
                VALUES (?, ?)
                """,
                (name.strip(), description)
            )
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a project by its ID.
        Args:
            project_id: The project ID.
        Returns:
            Project as a dict, or None if not found.
        """
        try:
            cursor = self.db_manager.execute_query(
                "SELECT id, name, description FROM projects WHERE id = ?",
                (project_id,)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "description": row[2]}
            return None
        except Exception as e:
            logger.error(f"Failed to get project by id: {e}")
            raise

    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a project by its name.
        Args:
            name: The project name.
        Returns:
            Project as a dict, or None if not found.
        """
        try:
            cursor = self.db_manager.execute_query(
                "SELECT id, name, description FROM projects WHERE name = ?",
                (name.strip(),)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "description": row[2]}
            return None
        except Exception as e:
            logger.error(f"Failed to get project by name: {e}")
            raise

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        Returns:
            List of project dicts.
        """
        try:
            cursor = self.db_manager.execute_query(
                "SELECT id, name, description FROM projects ORDER BY name ASC"
            )
            return [
                {"id": row[0], "name": row[1], "description": row[2]}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            raise

    def update_project(self, project_id: int, name: Optional[str] = None, description: Optional[str] = None) -> None:
        """
        Update a project's name and/or description.
        Args:
            project_id: The project ID.
            name: New name (optional).
            description: New description (optional).
        Raises:
            ValueError: If no update fields are provided or project does not exist.
        """
        if name is not None and not name.strip():
            raise ValueError("Project name cannot be empty.")
        if not self.get_project_by_id(project_id):
            raise ValueError(f"Project with id {project_id} does not exist.")
        fields = []
        values = []
        if name is not None:
            fields.append("name = ?")
            values.append(name.strip())
        if description is not None:
            fields.append("description = ?")
            values.append(description)
        if not fields:
            raise ValueError("No update fields provided.")
        values.append(project_id)
        try:
            self.db_manager.execute_query(
                f"UPDATE projects SET {', '.join(fields)} WHERE id = ?",
                tuple(values)
            )
        except Exception as e:
            logger.error(f"Failed to update project: {e}")
            raise

    def delete_project(self, project_id: int) -> None:
        """
        Delete a project by its ID.
        Args:
            project_id: The project ID.
        Raises:
            ValueError: If the project does not exist.
        """
        if not self.get_project_by_id(project_id):
            raise ValueError(f"Project with id {project_id} does not exist.")
        try:
            self.db_manager.execute_query(
                "DELETE FROM projects WHERE id = ?",
                (project_id,)
            )
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            raise 
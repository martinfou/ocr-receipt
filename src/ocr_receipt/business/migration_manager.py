"""
Migration Manager for OCR Invoice Parser.

This module provides a high-level interface for database migrations using yoyo-migrations,
integrated with the project's DatabaseManager architecture.
"""

import os
import logging
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from yoyo import read_migrations, get_backend
from yoyo.migrations import Migration

from .database_manager import DatabaseManager, DatabaseError


class MigrationError(Exception):
    """Custom exception for migration-related errors."""
    pass


class MigrationManager:
    """
    Manages database migrations using yoyo-migrations.
    
    This class provides a high-level interface for applying, rolling back,
    and querying database migrations, integrated with the project's
    DatabaseManager architecture.
    
    Usage:
        with DatabaseManager('mydb.sqlite') as db:
            migration_manager = MigrationManager(db, 'migrations/')
            migration_manager.apply_pending_migrations()
    """
    
    def __init__(self, database_manager: DatabaseManager, migrations_path: str = "migrations") -> None:
        """
        Initialize the MigrationManager.
        
        Args:
            database_manager: The DatabaseManager instance to use for database operations
            migrations_path: Path to the migrations directory
        """
        self.database_manager = database_manager
        self.migrations_path = Path(migrations_path)
        self.logger = logging.getLogger(__name__)
        
        if not self.migrations_path.exists():
            raise MigrationError(f"Migrations directory not found: {migrations_path}")
    
    def get_migration_status(self) -> List[Dict[str, Any]]:
        """
        Get the status of all migrations.
        
        Returns:
            List of dictionaries containing migration status information
        """
        try:
            backend = self._get_backend()
            migrations = read_migrations(str(self.migrations_path))
            
            status_list = []
            for migration in migrations:
                is_applied = backend.is_applied(migration)
                status_info = {
                    'id': migration.id,
                    'source': migration.source,
                    'is_applied': is_applied,
                    'status': 'A' if is_applied else 'U'
                }
                status_list.append(status_info)
            
            return status_list
        except Exception as e:
            self.logger.error(f"Failed to get migration status: {e}")
            raise MigrationError(f"Failed to get migration status: {e}")
    
    def apply_pending_migrations(self, force: bool = False) -> List[str]:
        """
        Apply all pending migrations.
        
        Args:
            force: If True, apply migrations without confirmation
            
        Returns:
            List of applied migration IDs
        """
        try:
            backend = self._get_backend()
            migrations = read_migrations(str(self.migrations_path))
            
            # Get pending migrations using the MigrationList filter method
            pending_migrations = migrations.filter(lambda m: not backend.is_applied(m))
            
            if not pending_migrations:
                self.logger.info("No pending migrations to apply")
                return []
            
            # Apply all pending migrations at once
            self.logger.info(f"Applying {len(pending_migrations)} pending migrations")
            backend.apply_migrations(pending_migrations, force=force)
            
            # Return the IDs of applied migrations
            applied_migrations = [m.id for m in pending_migrations]
            self.logger.info(f"Successfully applied migrations: {applied_migrations}")
            
            return applied_migrations
        except Exception as e:
            self.logger.error(f"Failed to apply migrations: {e}")
            raise MigrationError(f"Failed to apply migrations: {e}")
    
    def rollback_migrations(self, count: int = 1, force: bool = False) -> List[str]:
        """
        Rollback the specified number of migrations.
        
        Args:
            count: Number of migrations to rollback
            force: If True, rollback without confirmation
            
        Returns:
            List of rolled back migration IDs
        """
        try:
            backend = self._get_backend()
            migrations = read_migrations(str(self.migrations_path))
            
            # Get applied migrations using the MigrationList filter method
            applied_migrations = migrations.filter(lambda m: backend.is_applied(m))
            
            if not applied_migrations:
                self.logger.info("No applied migrations to rollback")
                return []
            
            # Reverse to get the most recent first
            applied_migrations.reverse()
            
            # Limit to requested count
            migrations_to_rollback = applied_migrations[:count]
            
            # Rollback all specified migrations at once
            self.logger.info(f"Rolling back {len(migrations_to_rollback)} migrations")
            backend.rollback_migrations(migrations_to_rollback, force=force)
            
            # Return the IDs of rolled back migrations
            rolled_back_migrations = [m.id for m in migrations_to_rollback]
            self.logger.info(f"Successfully rolled back migrations: {rolled_back_migrations}")
            
            return rolled_back_migrations
        except Exception as e:
            self.logger.error(f"Failed to rollback migrations: {e}")
            raise MigrationError(f"Failed to rollback migrations: {e}")
    
    def mark_migration_applied(self, migration_id: str) -> None:
        """
        Mark a migration as applied without running it.
        
        Args:
            migration_id: The ID of the migration to mark as applied
        """
        try:
            backend = self._get_backend()
            migrations = read_migrations(str(self.migrations_path))
            
            target_migration = None
            for migration in migrations:
                if migration.id == migration_id:
                    target_migration = migration
                    break
            
            if not target_migration:
                raise MigrationError(f"Migration not found: {migration_id}")
            
            if backend.is_applied(target_migration):
                self.logger.warning(f"Migration {migration_id} is already applied")
                return
            
            self.logger.info(f"Marking migration as applied: {migration_id}")
            backend.mark_migrations([target_migration])
            self.logger.info(f"Successfully marked migration as applied: {migration_id}")
        except Exception as e:
            self.logger.error(f"Failed to mark migration as applied: {e}")
            raise MigrationError(f"Failed to mark migration as applied: {e}")
    
    def get_pending_migrations(self) -> List[Dict[str, Any]]:
        """
        Get list of pending (unapplied) migrations.
        
        Returns:
            List of dictionaries containing pending migration information
        """
        status_list = self.get_migration_status()
        return [m for m in status_list if not m['is_applied']]
    
    def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """
        Get list of applied migrations.
        
        Returns:
            List of dictionaries containing applied migration information
        """
        status_list = self.get_migration_status()
        return [m for m in status_list if m['is_applied']]
    
    def is_database_initialized(self) -> bool:
        """
        Check if the database has been initialized with migrations.
        
        Returns:
            True if at least one migration has been applied, False otherwise
        """
        try:
            applied_migrations = self.get_applied_migrations()
            return len(applied_migrations) > 0
        except Exception:
            return False
    
    def _get_backend(self):
        """Get the yoyo backend for the database."""
        # Extract database path from DatabaseManager
        db_path = self.database_manager.db_path
        database_url = f"sqlite:///{db_path}"
        return get_backend(database_url)
    
    def _should_apply_migration(self, migration: Migration, force: bool) -> bool:
        """Determine if a migration should be applied."""
        if force:
            return True
        
        # In a real application, you might want to add confirmation logic here
        # For now, we'll apply automatically
        return True
    
    def _should_rollback_migration(self, migration: Migration, force: bool) -> bool:
        """Determine if a migration should be rolled back."""
        if force:
            return True
        
        # In a real application, you might want to add confirmation logic here
        # For now, we'll rollback automatically
        return True 
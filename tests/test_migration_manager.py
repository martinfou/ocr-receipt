"""
Unit tests for MigrationManager class.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from pathlib import Path

from ocr_receipt.business.migration_manager import MigrationManager, MigrationError
from ocr_receipt.business.database_manager import DatabaseManager


class TestMigrationManager:
    """Test cases for MigrationManager class."""

    @pytest.fixture
    def temp_migrations_dir(self):
        """Create a temporary migrations directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            migrations_dir = Path(temp_dir) / "migrations"
            migrations_dir.mkdir()
            
            # Create a simple test migration file
            migration_file = migrations_dir / "001_test_migration.py"
            migration_file.write_text("""
from yoyo import step
__depends__ = {}
steps = [step("CREATE TABLE test (id INTEGER);", "DROP TABLE test;")]
""")
            
            yield str(migrations_dir)

    @pytest.fixture
    def database_manager(self):
        """Create a database manager with in-memory database."""
        return DatabaseManager(":memory:")

    @pytest.fixture
    def migration_manager(self, database_manager, temp_migrations_dir):
        """Create a migration manager instance."""
        return MigrationManager(database_manager, temp_migrations_dir)

    def test_init_with_valid_migrations_path(self, database_manager, temp_migrations_dir):
        """Test initialization with valid migrations path."""
        migration_manager = MigrationManager(database_manager, temp_migrations_dir)
        assert migration_manager.migrations_path == Path(temp_migrations_dir)

    def test_init_with_invalid_migrations_path(self, database_manager):
        """Test initialization with invalid migrations path."""
        with pytest.raises(MigrationError, match="Migrations directory not found"):
            MigrationManager(database_manager, "/nonexistent/path")

    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_get_migration_status(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test getting migration status."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration1 = Mock()
        mock_migration1.id = "001_test_migration"
        mock_migration1.source = "migrations"
        
        mock_migration2 = Mock()
        mock_migration2.id = "002_another_migration"
        mock_migration2.source = "migrations"
        
        # Create a mock MigrationList object that can be iterated
        mock_migration_list = Mock()
        mock_migration_list.__iter__ = Mock(return_value=iter([mock_migration1, mock_migration2]))
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.side_effect = [True, False]
        
        # Test
        status = migration_manager.get_migration_status()
        
        # Assertions
        assert len(status) == 2
        assert status[0]['id'] == "001_test_migration"
        assert status[0]['is_applied'] is True
        assert status[0]['status'] == 'A'
        assert status[1]['id'] == "002_another_migration"
        assert status[1]['is_applied'] is False
        assert status[1]['status'] == 'U'
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_apply_pending_migrations(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test applying pending migrations."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration = Mock()
        mock_migration.id = "001_test_migration"
        
        # Create a mock MigrationList object
        mock_migration_list = Mock()
        mock_migration_list.filter.return_value = [mock_migration]
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.return_value = False
        mock_backend.to_apply.return_value = [mock_migration]
        
        # Test
        applied = migration_manager.apply_pending_migrations(force=True)
        
        # Assertions
        assert applied == ["001_test_migration"]
        mock_backend.apply_migrations.assert_called_once()
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_apply_pending_migrations_no_pending(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test applying migrations when none are pending."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration = Mock()
        # Create a mock MigrationList object
        mock_migration_list = Mock()
        mock_migration_list.filter.return_value = []  # No pending migrations
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.return_value = True  # All migrations already applied
        
        # Test
        applied = migration_manager.apply_pending_migrations()
        
        # Assertions
        assert applied == []
        mock_backend.apply_migrations.assert_not_called()
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_rollback_migrations(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test rolling back migrations."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration1 = Mock()
        mock_migration1.id = "001_test_migration"
        mock_migration2 = Mock()
        mock_migration2.id = "002_another_migration"
        
        # Create a mock MigrationList object
        mock_migration_list = Mock()
        mock_migration_list.filter.return_value = [mock_migration1, mock_migration2]
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.return_value = True  # Both migrations applied
        mock_backend.to_rollback.return_value = [mock_migration2]
        
        # Test
        rolled_back = migration_manager.rollback_migrations(count=1, force=True)
        
        # Assertions
        assert rolled_back == ["002_another_migration"]
        mock_backend.rollback_migrations.assert_called_once()
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_mark_migration_applied(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test marking a migration as applied."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration = Mock()
        mock_migration.id = "001_test_migration"
        
        # Create a mock MigrationList object that can be iterated
        mock_migration_list = Mock()
        mock_migration_list.__iter__ = Mock(return_value=iter([mock_migration]))
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.return_value = False  # Not yet applied
        
        # Test
        migration_manager.mark_migration_applied("001_test_migration")
        
        # Assertions
        mock_backend.mark_migrations.assert_called_once_with([mock_migration])
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_mark_migration_applied_not_found(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test marking a non-existent migration as applied."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration = Mock()
        mock_migration.id = "001_test_migration"
        
        # Create a mock MigrationList object that can be iterated
        mock_migration_list = Mock()
        mock_migration_list.__iter__ = Mock(return_value=iter([mock_migration]))
        mock_read_migrations.return_value = mock_migration_list
        
        # Test
        with pytest.raises(MigrationError, match="Migration not found"):
            migration_manager.mark_migration_applied("nonexistent_migration")
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_mark_migration_applied_already_applied(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test marking an already applied migration as applied."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration = Mock()
        mock_migration.id = "001_test_migration"
        
        # Create a mock MigrationList object that can be iterated
        mock_migration_list = Mock()
        mock_migration_list.__iter__ = Mock(return_value=iter([mock_migration]))
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.return_value = True  # Already applied
        
        # Test
        migration_manager.mark_migration_applied("001_test_migration")
        
        # Assertions - should not call mark_migrations since already applied
        mock_backend.mark_migrations.assert_not_called()
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_get_pending_migrations(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test getting pending migrations."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration1 = Mock()
        mock_migration1.id = "001_test_migration"
        mock_migration1.source = "migrations"
        
        mock_migration2 = Mock()
        mock_migration2.id = "002_another_migration"
        mock_migration2.source = "migrations"
        
        # Create a mock MigrationList object that can be iterated
        mock_migration_list = Mock()
        mock_migration_list.__iter__ = Mock(return_value=iter([mock_migration1, mock_migration2]))
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.side_effect = [True, False]
        
        # Test
        pending = migration_manager.get_pending_migrations()
        
        # Assertions
        assert len(pending) == 1
        assert pending[0]['id'] == "002_another_migration"
        assert pending[0]['is_applied'] is False
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_get_applied_migrations(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test getting applied migrations."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration1 = Mock()
        mock_migration1.id = "001_test_migration"
        mock_migration1.source = "migrations"
        
        mock_migration2 = Mock()
        mock_migration2.id = "002_another_migration"
        mock_migration2.source = "migrations"
        
        # Create a mock MigrationList object that can be iterated
        mock_migration_list = Mock()
        mock_migration_list.__iter__ = Mock(return_value=iter([mock_migration1, mock_migration2]))
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.side_effect = [True, False]
        
        # Test
        applied = migration_manager.get_applied_migrations()
        
        # Assertions
        assert len(applied) == 1
        assert applied[0]['id'] == "001_test_migration"
        assert applied[0]['is_applied'] is True
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_is_database_initialized_true(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test database initialization check when migrations are applied."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration = Mock()
        mock_migration.id = "001_test_migration"
        mock_migration.source = "migrations"
        
        # Create a mock MigrationList object that can be iterated
        mock_migration_list = Mock()
        mock_migration_list.__iter__ = Mock(return_value=iter([mock_migration]))
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.return_value = True
        
        # Test
        is_initialized = migration_manager.is_database_initialized()
        
        # Assertions
        assert is_initialized is True
    
    @patch('ocr_receipt.business.migration_manager.read_migrations')
    @patch('ocr_receipt.business.migration_manager.get_backend')
    def test_is_database_initialized_false(self, mock_get_backend, mock_read_migrations, migration_manager):
        """Test database initialization check when no migrations are applied."""
        # Mock setup
        mock_backend = Mock()
        mock_get_backend.return_value = mock_backend
        
        mock_migration = Mock()
        mock_migration.id = "001_test_migration"
        mock_migration.source = "migrations"
        
        # Create a mock MigrationList object that can be iterated
        mock_migration_list = Mock()
        mock_migration_list.__iter__ = Mock(return_value=iter([mock_migration]))
        mock_read_migrations.return_value = mock_migration_list
        mock_backend.is_applied.return_value = False
        
        # Test
        is_initialized = migration_manager.is_database_initialized()
        
        # Assertions
        assert is_initialized is False
    
    def test_get_backend(self, migration_manager):
        """Test getting the yoyo backend."""
        backend = migration_manager._get_backend()
        assert backend is not None
    
    def test_should_apply_migration_force_true(self, migration_manager):
        """Test should apply migration with force=True."""
        mock_migration = Mock()
        assert migration_manager._should_apply_migration(mock_migration, force=True) is True
    
    def test_should_apply_migration_force_false(self, migration_manager):
        """Test should apply migration with force=False."""
        mock_migration = Mock()
        assert migration_manager._should_apply_migration(mock_migration, force=False) is True
    
    def test_should_rollback_migration_force_true(self, migration_manager):
        """Test should rollback migration with force=True."""
        mock_migration = Mock()
        assert migration_manager._should_rollback_migration(mock_migration, force=True) is True
    
    def test_should_rollback_migration_force_false(self, migration_manager):
        """Test should rollback migration with force=False."""
        mock_migration = Mock()
        assert migration_manager._should_rollback_migration(mock_migration, force=False) is True 
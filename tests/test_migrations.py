"""
Direct tests for migration files using yoyo-migrations.
"""

import pytest
from yoyo import read_migrations, get_backend


def test_initial_schema_migration():
    """Test that the initial schema migration creates all expected tables."""
    # Use in-memory database to avoid file locking issues
    backend = get_backend('sqlite:///:memory:')
    migrations = read_migrations('migrations')
    backend.apply_migrations(backend.to_apply(migrations))

    # Get the connection from the backend to use with DatabaseManager
    connection = backend.connection

    # Test that all tables exist using the same connection
    cursor = connection.cursor()

    # Check businesses table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='businesses'")
    assert cursor.fetchone() is not None

    # Check business_keywords table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='business_keywords'")
    assert cursor.fetchone() is not None

    # Check projects table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
    assert cursor.fetchone() is not None

    # Check categories table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
    assert cursor.fetchone() is not None

    # Check invoice_metadata table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoice_metadata'")
    assert cursor.fetchone() is not None


def test_migration_schema_structure():
    """Test that the schema has the expected structure and constraints."""
    backend = get_backend('sqlite:///:memory:')
    migrations = read_migrations('migrations')
    backend.apply_migrations(backend.to_apply(migrations))

    cursor = backend.connection.cursor()

    # Test foreign key constraints exist
    cursor.execute("PRAGMA foreign_key_list(business_keywords)")
    fk_list = cursor.fetchall()
    assert len(fk_list) > 0  # Should have foreign key to businesses

    # Test indexes exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_business_keywords_keyword'")
    assert cursor.fetchone() is not None

    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_invoice_metadata_filename'")
    assert cursor.fetchone() is not None

    # Test table structure
    cursor.execute("PRAGMA table_info(businesses)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    assert 'id' in column_names
    assert 'name' in column_names
    assert 'created_at' in column_names
    assert 'updated_at' in column_names


def test_migration_rollback():
    """Test that migrations can be rolled back properly."""
    backend = get_backend('sqlite:///:memory:')
    migrations = read_migrations('migrations')
    
    # Apply migrations
    backend.apply_migrations(backend.to_apply(migrations))
    
    # Verify tables exist
    cursor = backend.connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='businesses'")
    assert cursor.fetchone() is not None
    
    # Rollback migrations
    backend.rollback_migrations(backend.to_rollback(migrations))
    
    # Verify tables are gone
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='businesses'")
    assert cursor.fetchone() is None 
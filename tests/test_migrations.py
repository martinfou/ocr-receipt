import pytest
from yoyo import read_migrations
from yoyo import get_backend

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
    
    # Test that category_code column exists (not cra_code)
    cursor.execute("PRAGMA table_info(categories)")
    columns = [row[1] for row in cursor.fetchall()]
    assert 'category_code' in columns
    assert 'cra_code' not in columns

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
    
    cursor.execute("PRAGMA foreign_key_list(invoice_metadata)")
    fk_list = cursor.fetchall()
    assert len(fk_list) > 0  # Should have foreign keys to projects and categories
    
    # Test indexes exist
    cursor.execute("PRAGMA index_list(business_keywords)")
    indexes = [row[1] for row in cursor.fetchall()]
    assert any('idx_business_keywords' in idx for idx in indexes)
    
    cursor.execute("PRAGMA index_list(invoice_metadata)")
    indexes = [row[1] for row in cursor.fetchall()]
    assert any('idx_invoice_metadata' in idx for idx in indexes) 
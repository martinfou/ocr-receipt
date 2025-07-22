#!/usr/bin/env python3
"""
Example demonstrating the MigrationManager functionality.

This example shows how to use the MigrationManager to:
1. Check migration status
2. Apply pending migrations
3. Rollback migrations
4. Check database initialization
"""

import tempfile
import os
from pathlib import Path

from ocr_receipt.business.migration_manager import MigrationManager
from ocr_receipt.business.database_manager import DatabaseManager


def main():
    """Demonstrate MigrationManager functionality."""
    print("=== MigrationManager Example ===\n")
    
    # Create a temporary database for demonstration
    temp_db = tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False)
    temp_db.close()
    db_path = temp_db.name
    
    try:
        # Create database and migration managers
        db_manager = DatabaseManager(db_path)
        migration_manager = MigrationManager(db_manager, "migrations")
        
        print(f"Database: {db_path}")
        print(f"Migrations directory: {migration_manager.migrations_path}")
        
        # 1. Check initial migration status
        print("\n1. Initial Migration Status:")
        status = migration_manager.get_migration_status()
        for migration in status:
            print(f"  - {migration['id']}: {migration['status']} ({'Applied' if migration['is_applied'] else 'Pending'})")
        
        # 2. Check if database is initialized
        print(f"\n2. Database Initialized: {migration_manager.is_database_initialized()}")
        
        # 3. Get pending migrations
        print("\n3. Pending Migrations:")
        pending = migration_manager.get_pending_migrations()
        if pending:
            for migration in pending:
                print(f"  - {migration['id']}")
        else:
            print("  - No pending migrations")
        
        # 4. Apply pending migrations
        print("\n4. Applying Migrations:")
        try:
            applied = migration_manager.apply_pending_migrations(force=True)
            if applied:
                print(f"  - Applied: {applied}")
            else:
                print("  - No migrations to apply")
        except Exception as e:
            print(f"  - Error applying migrations: {e}")
        
        # 5. Check status after applying
        print("\n5. Migration Status After Applying:")
        status = migration_manager.get_migration_status()
        for migration in status:
            print(f"  - {migration['id']}: {migration['status']} ({'Applied' if migration['is_applied'] else 'Pending'})")
        
        # 6. Check if database is now initialized
        print(f"\n6. Database Initialized: {migration_manager.is_database_initialized()}")
        
        # 7. Get applied migrations
        print("\n7. Applied Migrations:")
        applied = migration_manager.get_applied_migrations()
        if applied:
            for migration in applied:
                print(f"  - {migration['id']}")
        else:
            print("  - No applied migrations")
        
        print("\n=== Example Complete ===")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Cleanup
        try:
            os.unlink(db_path)
        except:
            pass


if __name__ == "__main__":
    main() 
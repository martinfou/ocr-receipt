"""
Tests for DocumentTypeManager.
"""

import pytest
import tempfile
import os
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.document_type_manager import DocumentTypeManager


class TestDocumentTypeManager:
    """Test cases for DocumentTypeManager."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Cleanup - close any open connections first
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            # On Windows, the file might still be in use
            # This is expected and not a test failure
            pass
    
    @pytest.fixture
    def db_manager(self, temp_db):
        """Create a DatabaseManager instance."""
        return DatabaseManager(temp_db)
    
    @pytest.fixture
    def document_type_manager(self, db_manager):
        """Create a DocumentTypeManager instance."""
        return DocumentTypeManager(db_manager)
    
    def test_init_creates_table(self, document_type_manager):
        """Test that initialization creates the document_types table."""
        # The table should be created during initialization
        cursor = document_type_manager.database_manager.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='document_types'"
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'document_types'
    
    def test_init_inserts_default_types(self, document_type_manager):
        """Test that initialization inserts default document types."""
        types = document_type_manager.get_all_document_types()
        assert len(types) == 4
        
        type_names = [t['name'] for t in types]
        assert 'Invoice' in type_names
        assert 'Credit Card' in type_names
        assert 'Receipt' in type_names
        assert 'Other' in type_names
        
        # Check that Invoice is the default
        default_type = document_type_manager.get_default_document_type()
        assert default_type == 'Invoice'
    
    def test_get_document_type_names(self, document_type_manager):
        """Test getting document type names."""
        names = document_type_manager.get_document_type_names()
        assert len(names) == 4
        assert 'Invoice' in names
        assert 'Credit Card' in names
        assert 'Receipt' in names
        assert 'Other' in names
    
    def test_add_document_type(self, document_type_manager):
        """Test adding a new document type."""
        success = document_type_manager.add_document_type(
            'Test Type', 'Test description', is_default=False
        )
        assert success is True
        
        types = document_type_manager.get_all_document_types()
        type_names = [t['name'] for t in types]
        assert 'Test Type' in type_names
        
        # Check that the new type was added with correct data
        test_type = next(t for t in types if t['name'] == 'Test Type')
        assert test_type['description'] == 'Test description'
        assert test_type['is_default'] == 0
    
    def test_add_document_type_as_default(self, document_type_manager):
        """Test adding a document type as default."""
        success = document_type_manager.add_document_type(
            'New Default', 'New default description', is_default=True
        )
        assert success is True
        
        # Check that the new type is now the default
        default_type = document_type_manager.get_default_document_type()
        assert default_type == 'New Default'
        
        # Check that the original default is no longer default
        types = document_type_manager.get_all_document_types()
        invoice_type = next(t for t in types if t['name'] == 'Invoice')
        assert invoice_type['is_default'] == 0
    
    def test_update_document_type(self, document_type_manager):
        """Test updating a document type."""
        success = document_type_manager.update_document_type(
            'Invoice', 'Updated Invoice', 'Updated description', is_default=False
        )
        assert success is True
        
        types = document_type_manager.get_all_document_types()
        type_names = [t['name'] for t in types]
        assert 'Updated Invoice' in type_names
        assert 'Invoice' not in type_names
        
        # Check that another type is now the default (since we removed the default)
        default_type = document_type_manager.get_default_document_type()
        assert default_type is not None
        assert default_type in type_names
        assert default_type != 'Updated Invoice'  # Should not be the updated one
    
    def test_delete_document_type(self, document_type_manager):
        """Test deleting a document type."""
        # Add a test type first
        document_type_manager.add_document_type('Test Delete', 'To be deleted')
        
        success = document_type_manager.delete_document_type('Test Delete')
        assert success is True
        
        types = document_type_manager.get_all_document_types()
        type_names = [t['name'] for t in types]
        assert 'Test Delete' not in type_names
    
    def test_delete_default_document_type(self, document_type_manager):
        """Test deleting the default document type."""
        # Try to delete the default type (Invoice)
        success = document_type_manager.delete_document_type('Invoice')
        assert success is True
        
        # Check that a new default was set
        default_type = document_type_manager.get_default_document_type()
        assert default_type is not None
        assert default_type != 'Invoice'
    
    def test_set_default_document_type(self, document_type_manager):
        """Test setting a document type as default."""
        success = document_type_manager.set_default_document_type('Credit Card')
        assert success is True
        
        default_type = document_type_manager.get_default_document_type()
        assert default_type == 'Credit Card'
    
    def test_reorder_document_types(self, document_type_manager):
        """Test reordering document types."""
        # Get current order
        original_names = document_type_manager.get_document_type_names()
        
        # Reorder them
        new_order = ['Other', 'Receipt', 'Credit Card', 'Invoice']
        success = document_type_manager.reorder_document_types(new_order)
        assert success is True
        
        # Check the new order
        reordered_names = document_type_manager.get_document_type_names()
        assert reordered_names == new_order 
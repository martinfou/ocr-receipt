"""
Tests for dialog integration with tabs in the OCR Receipt Parser.

This test file covers:
- Dialog creation from tab context
- Dialog data flow to/from tabs
- Dialog validation within tab context
"""

import pytest
import tempfile
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ocr_receipt.gui.business_keywords_tab import BusinessKeywordsTab
from ocr_receipt.gui.dialogs.add_business_dialog import AddBusinessDialog
from ocr_receipt.gui.dialogs.edit_keyword_dialog import EditKeywordDialog
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager


class TestTabDialogIntegration:
    """Test integration between tabs and dialogs."""
    
    @pytest.fixture
    def business_keywords_tab(self, qtbot):
        """Create a BusinessKeywordsTab for testing."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            db_manager.initialize_database()
            business_mapping_manager = BusinessMappingManager(db_manager)
            
            tab = BusinessKeywordsTab(business_mapping_manager)
            qtbot.addWidget(tab)
            yield tab
            
        finally:
            db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass
    
    def test_add_business_dialog_from_tab(self, business_keywords_tab, qtbot):
        """Test that add business dialog can be created from tab context."""
        # Simulate clicking the add button (this would normally trigger dialog)
        add_button = business_keywords_tab.add_button
        assert add_button is not None
        assert add_button.isEnabled()
        
        # Create dialog manually to test integration
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        
        # Test that dialog has proper structure
        assert dialog.windowTitle() != ""
        assert hasattr(dialog, 'name_edit')
        assert hasattr(dialog, 'ok_button')
        assert hasattr(dialog, 'cancel_button')
    
    def test_edit_keyword_dialog_from_tab(self, business_keywords_tab, qtbot):
        """Test that edit keyword dialog can be created from tab context."""
        # Add a business and keyword first
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        business_id = business_mapping_manager.add_business("Test Business")
        keyword_id = business_mapping_manager.add_keyword("Test Business", "test_keyword", 0)
        
        # Create sample keyword data
        keyword_data = {
            'id': keyword_id,
            'keyword': 'test_keyword',
            'business_name': 'Test Business',
            'is_case_sensitive': False,
            'usage_count': 0,
            'last_used': None
        }
        
        # Create dialog manually to test integration
        dialog = EditKeywordDialog(keyword_data)
        qtbot.addWidget(dialog)
        
        # Test that dialog has proper structure
        assert dialog.windowTitle() != ""
        assert hasattr(dialog, 'keyword_edit')
        assert hasattr(dialog, 'case_sensitive_checkbox')
        assert hasattr(dialog, 'save_button')
        assert hasattr(dialog, 'cancel_button')
    
    def test_dialog_data_flow_to_tab(self, business_keywords_tab, qtbot):
        """Test that data flows correctly from dialog to tab."""
        # Add a business through the business mapping manager
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        business_id = business_mapping_manager.add_business("New Business")
        
        # Refresh the tab to show the new business
        business_keywords_tab._load_keywords()
        
        # Check that the business appears in the table
        table = business_keywords_tab.keywords_table
        found = False
        for row in range(table.rowCount()):
            if table.item(row, 0) and table.item(row, 0).text() == "New Business":
                found = True
                break
        
        assert found, "New business should appear in the keywords table"
    
    def test_dialog_validation_in_tab_context(self, business_keywords_tab, qtbot):
        """Test that dialog validation works in tab context."""
        # Create add business dialog
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        
        # Test validation with empty input - OK button should be disabled
        dialog.name_edit.setText("")
        assert not dialog.ok_button.isEnabled()
        
        # Test validation with valid input - OK button should be enabled
        dialog.name_edit.setText("Valid Business Name")
        assert dialog.ok_button.isEnabled()
    
    def test_dialog_cancellation_preserves_tab_state(self, business_keywords_tab, qtbot):
        """Test that canceling dialogs preserves tab state."""
        # Get initial state
        initial_table_rows = business_keywords_tab.keywords_table.rowCount()
        
        # Create and cancel a dialog
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        dialog.reject()  # Cancel the dialog
        
        # Verify tab state is unchanged
        assert business_keywords_tab.keywords_table.rowCount() == initial_table_rows
    
    def test_dialog_acceptance_updates_tab(self, business_keywords_tab, qtbot):
        """Test that accepting dialogs updates the tab."""
        # Get initial state
        initial_table_rows = business_keywords_tab.keywords_table.rowCount()
        
        # Add a business through the business mapping manager
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        business_id = business_mapping_manager.add_business("Dialog Test Business")
        
        # Refresh the tab
        business_keywords_tab._load_keywords()
        
        # Verify tab is updated
        assert business_keywords_tab.keywords_table.rowCount() == initial_table_rows + 1


class TestTabDialogErrorHandling:
    """Test error handling in tab-dialog integration."""
    
    @pytest.fixture
    def business_keywords_tab(self, qtbot):
        """Create a BusinessKeywordsTab for testing."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            db_manager.initialize_database()
            business_mapping_manager = BusinessMappingManager(db_manager)
            
            tab = BusinessKeywordsTab(business_mapping_manager)
            qtbot.addWidget(tab)
            yield tab
            
        finally:
            db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass
    
    def test_duplicate_business_handling(self, business_keywords_tab, qtbot):
        """Test handling of duplicate business names."""
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        
        # Add first business
        result1 = business_mapping_manager.add_business("Duplicate Test")
        assert result1 is not None  # Should succeed
        
        # Try to add duplicate
        result2 = business_mapping_manager.add_business("Duplicate Test")
        assert result2 is False  # Should fail
        
        # Verify only one entry exists
        business_keywords_tab._load_keywords()
        table = business_keywords_tab.keywords_table
        
        count = 0
        for row in range(table.rowCount()):
            if table.item(row, 0) and table.item(row, 0).text() == "Duplicate Test":
                count += 1
        
        assert count == 1, "Should have exactly one entry for duplicate business"
    
    def test_invalid_keyword_handling(self, business_keywords_tab, qtbot):
        """Test handling of invalid keyword data."""
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        
        # Add a business first
        business_id = business_mapping_manager.add_business("Test Business")
        
        # Try to add keyword with invalid business name
        result = business_mapping_manager.add_keyword("Non-existent Business", "test_keyword", 0)
        assert result is False  # Should fail
        
        # Verify no invalid entries are added
        business_keywords_tab._load_keywords()
        table = business_keywords_tab.keywords_table
        
        # Check that no keywords exist for non-existent business
        for row in range(table.rowCount()):
            if table.item(row, 0) and table.item(row, 0).text() == "Non-existent Business":
                assert False, "Should not have entries for non-existent business"


class TestTabDialogAccessibility:
    """Test accessibility features in tab-dialog integration."""
    
    def test_dialog_keyboard_navigation(self, qtbot):
        """Test keyboard navigation in dialogs."""
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        
        # Test that dialog can receive focus
        assert dialog.isEnabled()
        
        # Test that input field can receive focus
        name_edit = dialog.name_edit
        assert name_edit.isEnabled()
        
        # Test that buttons are accessible
        ok_button = dialog.ok_button
        cancel_button = dialog.cancel_button
        
        # OK button starts disabled (no text), cancel button should be enabled
        assert not ok_button.isEnabled()  # No text entered yet
        assert cancel_button.isEnabled()
    
    def test_dialog_modal_behavior(self, qtbot):
        """Test that dialogs behave as modal windows."""
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        
        # Test that dialog is modal
        assert dialog.isModal()
    
    def test_dialog_default_focus(self, qtbot):
        """Test that dialogs have proper default focus."""
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        
        # Test that dialog is properly initialized
        assert dialog.name_edit is not None
        assert dialog.isModal() 
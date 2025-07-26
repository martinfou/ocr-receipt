"""
Integration tests for complete tab workflows in the OCR Receipt Parser.

This test file covers:
- Complete workflows from tab interaction to data persistence
- End-to-end scenarios involving multiple tabs
- Data consistency across tab operations
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


class TestCompleteTabWorkflows:
    """Test complete workflows involving tabs."""
    
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
    
    def test_complete_business_creation_workflow(self, business_keywords_tab, qtbot):
        """Test complete workflow of creating a business through the tab."""
        # Get initial state
        initial_count = business_keywords_tab.keywords_table.rowCount()
        
        # Create dialog and add business
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        
        # Enter business name
        qtbot.keyClicks(dialog.name_edit, "Test Business Workflow")
        qtbot.wait(100)
        
        # Verify OK button is enabled
        assert dialog.ok_button.isEnabled()
        
        # Accept the dialog
        qtbot.mouseClick(dialog.ok_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        
        # Verify dialog is closed
        assert not dialog.isVisible()
        
        # Get the business name from dialog
        business_name = dialog.get_business_name()
        assert business_name == "Test Business Workflow"
        
        # Add the business to the database
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        business_id = business_mapping_manager.add_business(business_name)
        assert business_id is not None
        
        # Refresh the tab
        business_keywords_tab._load_keywords()
        
        # Verify the business appears in the table
        table = business_keywords_tab.keywords_table
        assert table.rowCount() == initial_count + 1
        
        # Find the new business in the table
        found = False
        for row in range(table.rowCount()):
            if table.item(row, 0) and table.item(row, 0).text() == business_name:
                found = True
                break
        
        assert found, "New business should appear in the keywords table"
    
    def test_complete_keyword_management_workflow(self, business_keywords_tab, qtbot):
        """Test complete workflow of managing keywords through the tab."""
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        
        # Create a business first
        business_id = business_mapping_manager.add_business("Keyword Test Business")
        assert business_id is not None
        
        # Add a keyword
        keyword_id = business_mapping_manager.add_keyword("Keyword Test Business", "test_keyword", 0)
        assert keyword_id is not None
        
        # Refresh the tab
        business_keywords_tab._load_keywords()
        
        # Verify keyword appears in table
        table = business_keywords_tab.keywords_table
        found_keyword = False
        for row in range(table.rowCount()):
            if (table.item(row, 0) and table.item(row, 0).text() == "Keyword Test Business" and
                table.item(row, 1) and table.item(row, 1).text() == "test_keyword"):
                found_keyword = True
                break
        
        assert found_keyword, "Keyword should appear in the table"
        
        # Test editing the keyword
        keyword_data = {
            'id': keyword_id,
            'keyword': 'test_keyword',
            'business_name': 'Keyword Test Business',
            'is_case_sensitive': False,
            'usage_count': 0,
            'last_used': None
        }
        
        edit_dialog = EditKeywordDialog(keyword_data)
        qtbot.addWidget(edit_dialog)
        
        # Modify the keyword
        qtbot.keyClicks(edit_dialog.keyword_edit, "modified_keyword")
        qtbot.wait(100)
        
        # Accept the dialog
        qtbot.mouseClick(edit_dialog.save_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        
        # Verify dialog is closed
        assert not edit_dialog.isVisible()
    
    def test_data_persistence_across_tab_sessions(self, qtbot):
        """Test that data persists across different tab sessions."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            db_manager.initialize_database()
            business_mapping_manager = BusinessMappingManager(db_manager)
            
            # Add some data in first session
            business_id = business_mapping_manager.add_business("Persistent Business")
            keyword_id = business_mapping_manager.add_keyword("Persistent Business", "persistent_keyword", 1)
            
            # Create first tab session
            tab1 = BusinessKeywordsTab(business_mapping_manager)
            qtbot.addWidget(tab1)
            tab1._load_keywords()
            
            # Verify data is present
            table1 = tab1.keywords_table
            found_in_session1 = False
            for row in range(table1.rowCount()):
                if (table1.item(row, 0) and table1.item(row, 0).text() == "Persistent Business" and
                    table1.item(row, 1) and table1.item(row, 1).text() == "persistent_keyword"):
                    found_in_session1 = True
                    break
            
            assert found_in_session1, "Data should be present in first session"
            
            # Close first session
            tab1.close()
            
            # Create second tab session with same database
            tab2 = BusinessKeywordsTab(business_mapping_manager)
            qtbot.addWidget(tab2)
            tab2._load_keywords()
            
            # Verify data is still present
            table2 = tab2.keywords_table
            found_in_session2 = False
            for row in range(table2.rowCount()):
                if (table2.item(row, 0) and table2.item(row, 0).text() == "Persistent Business" and
                    table2.item(row, 1) and table2.item(row, 1).text() == "persistent_keyword"):
                    found_in_session2 = True
                    break
            
            assert found_in_session2, "Data should persist in second session"
            
        finally:
            db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass
    
    def test_tab_refresh_functionality(self, business_keywords_tab, qtbot):
        """Test that tab refresh functionality works correctly."""
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        
        # Get initial state
        initial_count = business_keywords_tab.keywords_table.rowCount()
        
        # Add data directly to database (simulating external changes)
        business_id = business_mapping_manager.add_business("Refresh Test Business")
        keyword_id = business_mapping_manager.add_keyword("Refresh Test Business", "refresh_keyword", 0)
        
        # Verify table hasn't changed yet (no refresh)
        assert business_keywords_tab.keywords_table.rowCount() == initial_count
        
        # Refresh the tab
        business_keywords_tab._load_keywords()
        
        # Verify table now shows the new data (should have at least one more row)
        new_count = business_keywords_tab.keywords_table.rowCount()
        assert new_count >= initial_count + 1, f"Expected at least {initial_count + 1} rows, got {new_count}"
        
        # Verify the new data is present
        table = business_keywords_tab.keywords_table
        found = False
        for row in range(table.rowCount()):
            if (table.item(row, 0) and table.item(row, 0).text() == "Refresh Test Business" and
                table.item(row, 1) and table.item(row, 1).text() == "refresh_keyword"):
                found = True
                break
        
        assert found, "Refreshed data should be visible in table"


class TestTabErrorRecovery:
    """Test error recovery scenarios in tab workflows."""
    
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
    
    def test_duplicate_business_error_recovery(self, business_keywords_tab, qtbot):
        """Test recovery from duplicate business errors."""
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        
        # Add first business
        business_id1 = business_mapping_manager.add_business("Duplicate Recovery Test")
        assert business_id1 is not None
        
        # Try to add duplicate
        business_id2 = business_mapping_manager.add_business("Duplicate Recovery Test")
        assert business_id2 is False  # Should fail
        
        # Verify only one entry exists
        business_keywords_tab._load_keywords()
        table = business_keywords_tab.keywords_table
        
        count = 0
        for row in range(table.rowCount()):
            if table.item(row, 0) and table.item(row, 0).text() == "Duplicate Recovery Test":
                count += 1
        
        assert count == 1, "Should have exactly one entry after duplicate attempt"
        
        # Verify tab is still functional
        assert business_keywords_tab.keywords_table.rowCount() >= 1
        assert business_keywords_tab.add_button.isEnabled()
    
    def test_invalid_data_error_recovery(self, business_keywords_tab, qtbot):
        """Test recovery from invalid data errors."""
        business_mapping_manager = business_keywords_tab.business_mapping_manager
        
        # Try to add keyword for non-existent business
        keyword_id = business_mapping_manager.add_keyword("Non-existent Business", "test_keyword", 0)
        assert keyword_id is False  # Should fail
        
        # Verify tab is still functional
        assert business_keywords_tab.keywords_table.rowCount() >= 0
        assert business_keywords_tab.add_button.isEnabled()
        
        # Verify no invalid data was added
        business_keywords_tab._load_keywords()
        table = business_keywords_tab.keywords_table
        
        for row in range(table.rowCount()):
            if table.item(row, 0) and table.item(row, 0).text() == "Non-existent Business":
                assert False, "Should not have entries for non-existent business"


class TestTabPerformance:
    """Test performance aspects of tab operations."""
    
    def test_tab_creation_performance(self, qtbot):
        """Test that tab creation is reasonably fast."""
        import time
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            db_manager.initialize_database()
            business_mapping_manager = BusinessMappingManager(db_manager)
            
            # Measure tab creation time
            start_time = time.time()
            tab = BusinessKeywordsTab(business_mapping_manager)
            qtbot.addWidget(tab)
            creation_time = time.time() - start_time
            
            # Tab creation should be reasonably fast (< 1 second)
            assert creation_time < 1.0, f"Tab creation took {creation_time:.2f} seconds"
            
        finally:
            db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass
    
    def test_tab_refresh_performance(self, qtbot):
        """Test that tab refresh is reasonably fast."""
        import time
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            db_manager.initialize_database()
            business_mapping_manager = BusinessMappingManager(db_manager)
            
            # Add some test data
            for i in range(10):
                business_mapping_manager.add_business(f"Performance Test Business {i}")
                business_mapping_manager.add_keyword(f"Performance Test Business {i}", f"keyword_{i}", 0)
            
            tab = BusinessKeywordsTab(business_mapping_manager)
            qtbot.addWidget(tab)
            
            # Measure refresh time
            start_time = time.time()
            tab._load_keywords()
            refresh_time = time.time() - start_time
            
            # Refresh should be reasonably fast (< 0.5 seconds)
            assert refresh_time < 0.5, f"Tab refresh took {refresh_time:.2f} seconds"
            
        finally:
            db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass 
"""
Comprehensive tests for all tabs in the OCR Receipt Parser main window.

This test file covers:
- Tab creation and initialization
- Tab navigation and switching
- Basic tab functionality
- Tab integration with main window
"""

import pytest
import tempfile
import os
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtCore import Qt

from ocr_receipt.gui.main_window import OCRMainWindow
from ocr_receipt.gui.single_pdf_tab import SinglePDFTab
from ocr_receipt.gui.business_keywords_tab import BusinessKeywordsTab
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
from ocr_receipt.business.project_manager import ProjectManager
from ocr_receipt.business.category_manager import CategoryManager


class TestMainWindowTabs:
    """Test the main window tab system."""
    
    @pytest.fixture
    def main_window(self, qapp, qtbot):
        """Create a main window for testing."""
        # Mock the config to return English language
        from unittest.mock import patch
        with patch('ocr_receipt.config.ConfigManager.get') as mock_get:
            def side_effect(key, default=None):
                if key == 'app.ui_language':
                    return 'en'
                elif key == 'gui.window_size':
                    return [1200, 800]
                elif key == 'database.path':
                    return 'ocr_receipts.db'
                return default
            mock_get.side_effect = side_effect
            
            window = OCRMainWindow()
            qtbot.addWidget(window)
            return window
    
    def test_tab_widget_creation(self, main_window):
        """Test that the tab widget is created correctly."""
        assert main_window.tab_widget is not None
        assert isinstance(main_window.tab_widget, QTabWidget)
        assert main_window.tab_widget.count() == 7  # Should have 7 tabs
    
    def test_tab_names(self, main_window):
        """Test that all expected tabs are present with correct names."""
        expected_tabs = [
            "Single PDF",
            "Business Keywords", 
            "Projects",
            "Categories",
            "Document Types",
            "File Naming",
            "Settings"
        ]
        
        for i, expected_name in enumerate(expected_tabs):
            assert main_window.tab_widget.tabText(i) == expected_name
    
    def test_tab_switching(self, main_window, qtbot):
        """Test that tabs can be switched between."""
        # Switch to each tab and verify it's selected
        for i in range(main_window.tab_widget.count()):
            main_window.tab_widget.setCurrentIndex(i)
            qtbot.wait(100)  # Small delay for UI update
            assert main_window.tab_widget.currentIndex() == i
    
    def test_tab_widgets_exist(self, main_window):
        """Test that each tab has a widget."""
        for i in range(main_window.tab_widget.count()):
            widget = main_window.tab_widget.widget(i)
            assert widget is not None


class TestSinglePDFTab:
    """Test the Single PDF tab functionality."""
    
    @pytest.fixture
    def single_pdf_tab(self, qapp, qtbot):
        """Create a SinglePDFTab for testing."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            db_manager.initialize_database()
            business_mapping_manager = BusinessMappingManager(db_manager)
            project_manager = ProjectManager(db_manager)
            category_manager = CategoryManager(db_manager)
            
            tab = SinglePDFTab(
                business_mapping_manager=business_mapping_manager,
                project_manager=project_manager,
                category_manager=category_manager
            )
            qtbot.addWidget(tab)
            yield tab
            
        finally:
            db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass
    
    def test_single_pdf_tab_creation(self, single_pdf_tab):
        """Test that SinglePDFTab is created with all required components."""
        assert single_pdf_tab is not None
        assert hasattr(single_pdf_tab, 'file_path_edit')
        assert hasattr(single_pdf_tab, 'pdf_preview')
        assert hasattr(single_pdf_tab, 'data_panel')
        assert hasattr(single_pdf_tab, 'browse_rename_button')
        assert hasattr(single_pdf_tab, 'ocr_button')
        assert hasattr(single_pdf_tab, 'rename_button')
        assert hasattr(single_pdf_tab, 'raw_data_button')
    
    def test_file_path_edit_functionality(self, single_pdf_tab, qtbot):
        """Test file path edit functionality."""
        test_path = "/test/path/to/document.pdf"
        single_pdf_tab.file_path_edit.setText(test_path)
        assert single_pdf_tab.file_path_edit.text() == test_path
    
    def test_data_panel_components(self, single_pdf_tab):
        """Test that data panel has all required components."""
        panel = single_pdf_tab.data_panel
        assert hasattr(panel, 'company_edit')
        assert hasattr(panel, 'total_edit')
        assert hasattr(panel, 'date_edit')
        assert hasattr(panel, 'invoice_number_edit')
    
    def test_data_panel_editing(self, single_pdf_tab, qtbot):
        """Test that data panel fields are editable."""
        panel = single_pdf_tab.data_panel
        
        # Test company field (now EditableComboBox)
        panel.company_edit.setCurrentText("Test Company")
        assert panel.company_edit.currentText() == "Test Company"
        
        # Test total field
        panel.total_edit.setText("123.45")
        assert panel.total_edit.text() == "123.45"
        
        # Test date field
        panel.date_edit.setText("2024-01-15")
        assert panel.date_edit.text() == "2024-01-15"
        
        # Test invoice number field
        panel.invoice_number_edit.setText("INV-001")
        assert panel.invoice_number_edit.text() == "INV-001"


class TestBusinessKeywordsTab:
    """Test the Business Keywords tab functionality."""
    
    @pytest.fixture
    def business_keywords_tab(self, qapp, qtbot):
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
    
    def test_business_keywords_tab_creation(self, business_keywords_tab):
        """Test that BusinessKeywordsTab is created with all required components."""
        assert business_keywords_tab is not None
        assert hasattr(business_keywords_tab, 'keywords_table')
        assert hasattr(business_keywords_tab, 'add_button')
        assert hasattr(business_keywords_tab, 'edit_button')
        assert hasattr(business_keywords_tab, 'delete_button')
        assert hasattr(business_keywords_tab, 'refresh_button')
    
    def test_keywords_table_initialization(self, business_keywords_tab):
        """Test that keywords table is properly initialized."""
        table = business_keywords_tab.keywords_table
        assert table is not None
        assert table.rowCount() >= 0  # Should be 0 or more
        assert table.columnCount() > 0  # Should have columns
    
    def test_add_button_functionality(self, business_keywords_tab, qtbot):
        """Test that add button is clickable."""
        button = business_keywords_tab.add_button
        assert button.isEnabled()
        assert button.text() != ""
    
    def test_edit_button_functionality(self, business_keywords_tab, qtbot):
        """Test that edit button exists and is properly configured."""
        button = business_keywords_tab.edit_button
        assert button is not None
        assert button.text() != ""
    
    def test_delete_button_functionality(self, business_keywords_tab, qtbot):
        """Test that delete button exists and is properly configured."""
        button = business_keywords_tab.delete_button
        assert button is not None
        assert button.text() != ""


class TestPlaceholderTabs:
    """Test the placeholder tabs (Projects, Categories, File Naming, Settings)."""
    
    @pytest.fixture
    def main_window(self, qapp, qtbot):
        """Create a main window for testing placeholder tabs."""
        window = OCRMainWindow()
        qtbot.addWidget(window)
        return window
    
    def test_projects_tab_placeholder(self, main_window):
        """Test that Projects tab exists and has placeholder content."""
        projects_widget = main_window.tab_widget.widget(2)  # Index 2 is Projects tab
        assert projects_widget is not None
        
        # Check for placeholder label
        layout = projects_widget.layout()
        assert layout is not None
        assert layout.count() > 0
    
    def test_categories_tab_placeholder(self, main_window):
        """Test that Categories tab exists and has placeholder content."""
        categories_widget = main_window.tab_widget.widget(3)  # Index 3 is Categories tab
        assert categories_widget is not None
        
        # Check for placeholder label
        layout = categories_widget.layout()
        assert layout is not None
        assert layout.count() > 0
    
    def test_file_naming_tab_placeholder(self, main_window):
        """Test that File Naming tab exists and has placeholder content."""
        file_naming_widget = main_window.tab_widget.widget(4)  # Index 4 is File Naming tab
        assert file_naming_widget is not None
        
        # Check for placeholder label
        layout = file_naming_widget.layout()
        assert layout is not None
        assert layout.count() > 0
    
    def test_settings_tab_placeholder(self, main_window):
        """Test that Settings tab exists and has placeholder content."""
        settings_widget = main_window.tab_widget.widget(5)  # Index 5 is Settings tab
        assert settings_widget is not None
        
        # Check for placeholder label
        layout = settings_widget.layout()
        assert layout is not None
        assert layout.count() > 0


class TestTabIntegration:
    """Test integration between tabs and main window."""
    
    @pytest.fixture
    def main_window(self, qapp, qtbot):
        """Create a main window for integration testing."""
        window = OCRMainWindow()
        qtbot.addWidget(window)
        return window
    
    def test_tab_switching_preserves_state(self, main_window, qtbot):
        """Test that switching between tabs preserves their state."""
        # Switch to Single PDF tab and set some data
        main_window.tab_widget.setCurrentIndex(0)
        single_pdf_tab = main_window.tab_widget.widget(0)
        if hasattr(single_pdf_tab, 'file_path_edit'):
            single_pdf_tab.file_path_edit.setText("test.pdf")
        
        # Switch to Business Keywords tab
        main_window.tab_widget.setCurrentIndex(1)
        qtbot.wait(100)
        
        # Switch back to Single PDF tab
        main_window.tab_widget.setCurrentIndex(0)
        qtbot.wait(100)
        
        # Verify the data is still there
        if hasattr(single_pdf_tab, 'file_path_edit'):
            assert single_pdf_tab.file_path_edit.text() == "test.pdf"
    
    def test_tab_widget_responsive(self, main_window, qtbot):
        """Test that tab widget responds to user interactions."""
        # Test that we can programmatically change tabs
        for i in range(main_window.tab_widget.count()):
            main_window.tab_widget.setCurrentIndex(i)
            qtbot.wait(50)
            assert main_window.tab_widget.currentIndex() == i
    
    def test_tab_widget_accessible(self, main_window):
        """Test that tab widget is accessible and properly configured."""
        tab_widget = main_window.tab_widget
        assert tab_widget.isEnabled()
        assert tab_widget.count() > 0 
"""
Simple tests for tab functionality in the OCR Receipt Parser.

This test file focuses on testing individual tab components without
importing the full main window to avoid dependency issues.
"""

import pytest
import tempfile
import os
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel

from ocr_receipt.gui.business_keywords_tab import BusinessKeywordsTab
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager


class TestTabWidgetBasics:
    """Test basic tab widget functionality."""
    
    @pytest.fixture
    def tab_widget(self, qtbot):
        """Create a basic tab widget for testing."""
        widget = QTabWidget()
        qtbot.addWidget(widget)
        return widget
    
    def test_tab_widget_creation(self, tab_widget):
        """Test that tab widget is created correctly."""
        assert tab_widget is not None
        assert tab_widget.count() == 0  # Should start empty
    
    def test_add_tab(self, tab_widget):
        """Test adding tabs to the widget."""
        # Create a simple widget for the tab
        tab_content = QWidget()
        layout = QVBoxLayout(tab_content)
        layout.addWidget(QLabel("Test Tab Content"))
        
        # Add the tab
        tab_widget.addTab(tab_content, "Test Tab")
        
        assert tab_widget.count() == 1
        assert tab_widget.tabText(0) == "Test Tab"
    
    def test_switch_tabs(self, tab_widget, qtbot):
        """Test switching between tabs."""
        # Add multiple tabs
        for i in range(3):
            tab_content = QWidget()
            layout = QVBoxLayout(tab_content)
            layout.addWidget(QLabel(f"Tab {i} Content"))
            tab_widget.addTab(tab_content, f"Tab {i}")
        
        assert tab_widget.count() == 3
        
        # Switch to each tab
        for i in range(3):
            tab_widget.setCurrentIndex(i)
            qtbot.wait(50)
            assert tab_widget.currentIndex() == i


class TestBusinessKeywordsTabSimple:
    """Test the Business Keywords tab with simplified setup."""
    
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
    
    def test_tab_creation(self, business_keywords_tab):
        """Test that BusinessKeywordsTab is created successfully."""
        assert business_keywords_tab is not None
        assert hasattr(business_keywords_tab, 'keywords_table')
        assert hasattr(business_keywords_tab, 'add_button')
        assert hasattr(business_keywords_tab, 'edit_button')
        assert hasattr(business_keywords_tab, 'delete_button')
    
    def test_keywords_table_exists(self, business_keywords_tab):
        """Test that keywords table is properly initialized."""
        table = business_keywords_tab.keywords_table
        assert table is not None
        assert table.rowCount() >= 0
        assert table.columnCount() > 0
    
    def test_buttons_exist(self, business_keywords_tab):
        """Test that all required buttons exist."""
        assert business_keywords_tab.add_button is not None
        assert business_keywords_tab.edit_button is not None
        assert business_keywords_tab.delete_button is not None
    
    def test_button_texts(self, business_keywords_tab):
        """Test that buttons have appropriate text."""
        assert business_keywords_tab.add_button.text() != ""
        assert business_keywords_tab.edit_button.text() != ""
        assert business_keywords_tab.delete_button.text() != ""


class TestPlaceholderTabStructure:
    """Test the structure of placeholder tabs."""
    
    def test_placeholder_tab_creation(self, qtbot):
        """Test creating a placeholder tab structure."""
        # Create a tab widget
        tab_widget = QTabWidget()
        qtbot.addWidget(tab_widget)
        
        # Create a placeholder tab (similar to what main window does)
        placeholder_widget = QWidget()
        layout = QVBoxLayout(placeholder_widget)
        layout.addWidget(QLabel("Placeholder Tab Content"))
        
        # Add the tab
        tab_widget.addTab(placeholder_widget, "Placeholder Tab")
        
        assert tab_widget.count() == 1
        assert tab_widget.tabText(0) == "Placeholder Tab"
        
        # Verify the widget structure
        widget = tab_widget.widget(0)
        assert widget is not None
        assert widget.layout() is not None
        assert widget.layout().count() > 0


class TestTabNavigation:
    """Test tab navigation functionality."""
    
    @pytest.fixture
    def multi_tab_widget(self, qtbot):
        """Create a tab widget with multiple tabs."""
        tab_widget = QTabWidget()
        qtbot.addWidget(tab_widget)
        
        # Add several tabs
        tab_names = ["Tab 1", "Tab 2", "Tab 3", "Tab 4"]
        for name in tab_names:
            tab_content = QWidget()
            layout = QVBoxLayout(tab_content)
            layout.addWidget(QLabel(f"Content for {name}"))
            tab_widget.addTab(tab_content, name)
        
        return tab_widget
    
    def test_tab_count(self, multi_tab_widget):
        """Test that all tabs are added correctly."""
        assert multi_tab_widget.count() == 4
    
    def test_tab_names(self, multi_tab_widget):
        """Test that tab names are correct."""
        expected_names = ["Tab 1", "Tab 2", "Tab 3", "Tab 4"]
        for i, expected_name in enumerate(expected_names):
            assert multi_tab_widget.tabText(i) == expected_name
    
    def test_tab_switching(self, multi_tab_widget, qtbot):
        """Test switching between tabs."""
        for i in range(multi_tab_widget.count()):
            multi_tab_widget.setCurrentIndex(i)
            qtbot.wait(50)
            assert multi_tab_widget.currentIndex() == i
    
    def test_tab_widgets_accessible(self, multi_tab_widget):
        """Test that all tab widgets are accessible."""
        for i in range(multi_tab_widget.count()):
            widget = multi_tab_widget.widget(i)
            assert widget is not None


class TestTabIntegrationSimple:
    """Test simple tab integration scenarios."""
    
    def test_tab_state_preservation(self, qtbot):
        """Test that tab state is preserved when switching."""
        tab_widget = QTabWidget()
        qtbot.addWidget(tab_widget)
        
        # Create tabs with some state
        tab1_content = QWidget()
        layout1 = QVBoxLayout(tab1_content)
        label1 = QLabel("Initial State")
        layout1.addWidget(label1)
        tab_widget.addTab(tab1_content, "Tab 1")
        
        tab2_content = QWidget()
        layout2 = QVBoxLayout(tab2_content)
        label2 = QLabel("Tab 2 Content")
        layout2.addWidget(label2)
        tab_widget.addTab(tab2_content, "Tab 2")
        
        # Switch to tab 1 and modify state
        tab_widget.setCurrentIndex(0)
        label1.setText("Modified State")
        
        # Switch to tab 2
        tab_widget.setCurrentIndex(1)
        qtbot.wait(50)
        
        # Switch back to tab 1
        tab_widget.setCurrentIndex(0)
        qtbot.wait(50)
        
        # Verify state is preserved
        assert label1.text() == "Modified State"
    
    def test_tab_widget_responsiveness(self, qtbot):
        """Test that tab widget responds to programmatic changes."""
        tab_widget = QTabWidget()
        qtbot.addWidget(tab_widget)
        
        # Add a tab
        tab_content = QWidget()
        layout = QVBoxLayout(tab_content)
        layout.addWidget(QLabel("Test Content"))
        tab_widget.addTab(tab_content, "Test Tab")
        
        # Test responsiveness
        assert tab_widget.isEnabled()
        assert tab_widget.count() == 1 
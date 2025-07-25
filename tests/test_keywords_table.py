"""
Tests for the KeywordsTable widget.
"""

import pytest
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from src.ocr_receipt.gui.widgets.keywords_table import KeywordsTable

@pytest.fixture
def app():
    """Create a QApplication instance for testing."""
    return QApplication([])

@pytest.fixture
def parent_widget(app):
    """Create a parent widget for the KeywordsTable."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    return widget

@pytest.fixture
def keywords_table(parent_widget):
    """Create a KeywordsTable instance."""
    return KeywordsTable(parent_widget)

@pytest.fixture
def sample_keywords():
    """Sample keyword data for testing."""
    return [
        {
            "business_name": "Test Business 1",
            "keyword": "test1",
            "is_case_sensitive": 0,
            "usage_count": 5,
            "last_used": "2024-01-15 10:30:00"
        },
        {
            "business_name": "Test Business 2", 
            "keyword": "TEST2",
            "is_case_sensitive": 1,
            "usage_count": 10,
            "last_used": "2024-01-16 14:20:00"
        },
        {
            "business_name": "Test Business 1",
            "keyword": "another_keyword",
            "is_case_sensitive": 0,
            "usage_count": 0,
            "last_used": None
        }
    ]

class TestKeywordsTable:
    """Test cases for KeywordsTable widget."""

    def test_initialization(self, keywords_table):
        """Test that the table initializes correctly."""
        assert keywords_table.columnCount() == 6
        assert keywords_table.horizontalHeaderItem(0).text() == "Business"
        assert keywords_table.horizontalHeaderItem(1).text() == "Keyword"
        assert keywords_table.horizontalHeaderItem(2).text() == "Match Type"
        assert keywords_table.horizontalHeaderItem(3).text() == "Case Sensitive"
        assert keywords_table.horizontalHeaderItem(4).text() == "Usage Count"
        assert keywords_table.horizontalHeaderItem(5).text() == "Last Used"

    def test_load_keywords(self, keywords_table, sample_keywords):
        """Test loading keywords into the table."""
        keywords_table.load_keywords(sample_keywords)
        
        assert keywords_table.rowCount() == 3
        
        # Check first row
        assert keywords_table.item(0, 0).text() == "Test Business 1"
        assert keywords_table.item(0, 1).text() == "test1"
        assert keywords_table.item(0, 2).text() == "fuzzy"
        assert keywords_table.item(0, 3).text() == "No"
        assert keywords_table.item(0, 4).text() == "5"
        assert keywords_table.item(0, 5).text() == "2024-01-15 10:30:00"
        
        # Check second row
        assert keywords_table.item(1, 0).text() == "Test Business 2"
        assert keywords_table.item(1, 1).text() == "TEST2"
        assert keywords_table.item(1, 2).text() == "exact"
        assert keywords_table.item(1, 3).text() == "Yes"
        assert keywords_table.item(1, 4).text() == "10"
        assert keywords_table.item(1, 5).text() == "2024-01-16 14:20:00"
        
        # Check third row (no last_used)
        assert keywords_table.item(2, 5).text() == "Never"

    def test_selection_handling(self, keywords_table, sample_keywords):
        """Test selection handling."""
        keywords_table.load_keywords(sample_keywords)
        
        # Test single selection
        keywords_table.selectRow(0)
        selected = keywords_table.get_selected_keywords()
        assert len(selected) == 1
        assert selected[0]["keyword"] == "test1"
        
        # Test single keyword getter
        selected_keyword = keywords_table.get_selected_keyword()
        assert selected_keyword["keyword"] == "test1"

    def test_no_selection(self, keywords_table, sample_keywords):
        """Test behavior when no rows are selected."""
        keywords_table.load_keywords(sample_keywords)
        
        selected = keywords_table.get_selected_keywords()
        assert len(selected) == 0
        
        selected_keyword = keywords_table.get_selected_keyword()
        assert selected_keyword is None

    def test_select_specific_keyword(self, keywords_table, sample_keywords):
        """Test selecting a specific keyword."""
        keywords_table.load_keywords(sample_keywords)
        
        # Select by keyword and business name
        success = keywords_table.select_keyword("TEST2", "Test Business 2")
        assert success is True
        
        selected = keywords_table.get_selected_keyword()
        assert selected["keyword"] == "TEST2"
        assert selected["business_name"] == "Test Business 2"

    def test_select_nonexistent_keyword(self, keywords_table, sample_keywords):
        """Test selecting a keyword that doesn't exist."""
        keywords_table.load_keywords(sample_keywords)
        
        success = keywords_table.select_keyword("nonexistent", "Test Business 1")
        assert success is False

    def test_filter_widgets_setup(self, parent_widget):
        """Test that filter widgets are set up correctly."""
        keywords_table = KeywordsTable(parent_widget)
        keywords_table._setup_filter_widgets(parent_widget)
        
        # Check that filter widgets exist
        assert hasattr(keywords_table, 'search_filter')
        assert hasattr(keywords_table, 'business_filter')
        assert hasattr(keywords_table, 'match_type_filter')
        assert hasattr(keywords_table, 'clear_filters_btn')
        
        # Check filter widget properties
        assert keywords_table.search_filter.placeholderText() == "Search keywords or businesses..."
        assert keywords_table.business_filter.count() == 1  # "All Businesses"
        assert keywords_table.match_type_filter.count() == 3  # "All Types", "exact", "fuzzy"

    def test_search_filter(self, keywords_table, sample_keywords):
        """Test search filtering functionality."""
        keywords_table.load_keywords(sample_keywords)
        keywords_table._setup_filter_widgets(keywords_table.parent())
        
        # Test search by keyword
        keywords_table.search_filter.setText("test1")
        keywords_table._apply_filters()
        assert keywords_table.rowCount() == 1
        assert keywords_table.item(0, 1).text() == "test1"
        
        # Test search by business name
        keywords_table.search_filter.setText("Test Business 2")
        keywords_table._apply_filters()
        assert keywords_table.rowCount() == 1
        assert keywords_table.item(0, 0).text() == "Test Business 2"
        
        # Test search with no results
        keywords_table.search_filter.setText("nonexistent")
        keywords_table._apply_filters()
        assert keywords_table.rowCount() == 0

    def test_business_filter(self, keywords_table, sample_keywords):
        """Test business filtering functionality."""
        keywords_table.load_keywords(sample_keywords)
        keywords_table._setup_filter_widgets(keywords_table.parent())
        
        # Test filtering by business
        keywords_table.business_filter.setCurrentText("Test Business 1")
        keywords_table._apply_filters()
        assert keywords_table.rowCount() == 2
        assert all(keywords_table.item(i, 0).text() == "Test Business 1" for i in range(2))

    def test_match_type_filter(self, keywords_table, sample_keywords):
        """Test match type filtering functionality."""
        keywords_table.load_keywords(sample_keywords)
        keywords_table._setup_filter_widgets(keywords_table.parent())
        
        # Test filtering by exact matches
        keywords_table.match_type_filter.setCurrentText("exact")
        keywords_table._apply_filters()
        assert keywords_table.rowCount() == 1
        assert keywords_table.item(0, 2).text() == "exact"
        
        # Test filtering by fuzzy matches
        keywords_table.match_type_filter.setCurrentText("fuzzy")
        keywords_table._apply_filters()
        assert keywords_table.rowCount() == 2
        assert all(keywords_table.item(i, 2).text() == "fuzzy" for i in range(2))

    def test_clear_filters(self, keywords_table, sample_keywords):
        """Test clearing all filters."""
        keywords_table.load_keywords(sample_keywords)
        keywords_table._setup_filter_widgets(keywords_table.parent())
        
        # Apply some filters
        keywords_table.search_filter.setText("test1")
        keywords_table._apply_filters()
        assert keywords_table.rowCount() == 1
        
        # Clear filters
        keywords_table._clear_filters()
        assert keywords_table.rowCount() == 3
        assert keywords_table.search_filter.text() == ""

    def test_sorting(self, keywords_table, sample_keywords):
        """Test table sorting functionality."""
        keywords_table.load_keywords(sample_keywords)
        
        # Test sorting by usage count (column 4)
        keywords_table.sortItems(4, Qt.SortOrder.DescendingOrder)
        
        # Should be sorted by usage count descending
        usage_counts = [int(keywords_table.item(i, 4).text()) for i in range(keywords_table.rowCount())]
        assert usage_counts == [10, 5, 0]

    def test_refresh(self, keywords_table, sample_keywords):
        """Test table refresh functionality."""
        keywords_table.load_keywords(sample_keywords)
        initial_row_count = keywords_table.rowCount()
        
        keywords_table.refresh()
        assert keywords_table.rowCount() == initial_row_count

    def test_get_filter_widgets(self, parent_widget):
        """Test getting filter widgets."""
        keywords_table = KeywordsTable(parent_widget)
        keywords_table._setup_filter_widgets(parent_widget)
        
        widgets = keywords_table.get_filter_widgets()
        assert 'search_filter' in widgets
        assert 'business_filter' in widgets
        assert 'match_type_filter' in widgets
        assert 'clear_filters_btn' in widgets

    def test_signals(self, keywords_table, sample_keywords, qtbot):
        """Test that signals are emitted correctly."""
        keywords_table.load_keywords(sample_keywords)
        
        # Test selection changed signal
        with qtbot.waitSignal(keywords_table.selection_changed):
            keywords_table.selectRow(0)
        
        # Test keyword selected signal
        with qtbot.waitSignal(keywords_table.keyword_selected):
            keywords_table._edit_selected_keyword()

    def test_context_menu(self, keywords_table, sample_keywords, qtbot):
        """Test context menu functionality."""
        keywords_table.load_keywords(sample_keywords)
        
        # Right-click on first row
        keywords_table.selectRow(0)
        keywords_table.contextMenuEvent(None)  # This would normally be called by Qt
        
        # The context menu should be created (we can't easily test its execution in unit tests)
        # This test mainly ensures the method doesn't crash

    def test_alternating_row_colors(self, keywords_table):
        """Test that alternating row colors are enabled."""
        assert keywords_table.alternatingRowColors() is True

    def test_selection_mode(self, keywords_table):
        """Test that extended selection mode is enabled."""
        assert keywords_table.selectionMode() == keywords_table.SelectionMode.ExtendedSelection

    def test_edit_triggers(self, keywords_table):
        """Test that editing is disabled."""
        assert keywords_table.editTriggers() == keywords_table.EditTrigger.NoEditTriggers 
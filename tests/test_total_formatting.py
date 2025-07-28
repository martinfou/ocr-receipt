"""
Test total amount formatting functionality.
"""

import pytest
from ocr_receipt.gui.widgets.data_panel import DataPanel


@pytest.fixture
def data_panel(qapp):
    """Create a DataPanel instance for testing."""
    return DataPanel()


class TestTotalFormatting:
    """Test total amount formatting with 2 decimal places."""
    
    def test_total_formatting_with_integer(self, data_panel):
        """Test that integer totals are formatted with 2 decimal places."""
        data = {
            "total": 44,
            "total_confidence": 1.0
        }
        data_panel.load_data(data)
        assert data_panel.total_edit.text() == "44.00"
    
    def test_total_formatting_with_float(self, data_panel):
        """Test that float totals are formatted with 2 decimal places."""
        data = {
            "total": 44.5,
            "total_confidence": 1.0
        }
        data_panel.load_data(data)
        assert data_panel.total_edit.text() == "44.50"
    
    def test_total_formatting_with_string_float(self, data_panel):
        """Test that string float totals are formatted with 2 decimal places."""
        data = {
            "total": "44.5",
            "total_confidence": 1.0
        }
        data_panel.load_data(data)
        assert data_panel.total_edit.text() == "44.50"
    
    def test_total_formatting_with_string_integer(self, data_panel):
        """Test that string integer totals are formatted with 2 decimal places."""
        data = {
            "total": "44",
            "total_confidence": 1.0
        }
        data_panel.load_data(data)
        assert data_panel.total_edit.text() == "44.00"
    
    def test_total_formatting_with_already_formatted(self, data_panel):
        """Test that already formatted totals remain correct."""
        data = {
            "total": "44.00",
            "total_confidence": 1.0
        }
        data_panel.load_data(data)
        assert data_panel.total_edit.text() == "44.00"
    
    def test_total_formatting_with_empty_value(self, data_panel):
        """Test that empty total values are handled correctly."""
        data = {
            "total": "",
            "total_confidence": 1.0
        }
        data_panel.load_data(data)
        assert data_panel.total_edit.text() == ""
    
    def test_total_formatting_with_invalid_value(self, data_panel):
        """Test that invalid total values are handled gracefully."""
        data = {
            "total": "invalid",
            "total_confidence": 1.0
        }
        data_panel.load_data(data)
        assert data_panel.total_edit.text() == "invalid"
    
    def test_total_formatting_with_none_value(self, data_panel):
        """Test that None total values are handled correctly."""
        data = {
            "total": None,
            "total_confidence": 1.0
        }
        data_panel.load_data(data)
        assert data_panel.total_edit.text() == "" 
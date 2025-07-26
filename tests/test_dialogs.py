"""
Tests for dialog components.
"""

import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from ocr_receipt.gui.dialogs.add_business_dialog import AddBusinessDialog
from ocr_receipt.gui.dialogs.edit_keyword_dialog import EditKeywordDialog

@pytest.fixture
def sample_keyword_data():
    """Sample keyword data for testing EditKeywordDialog."""
    return {
        "business_name": "Test Business",
        "keyword": "test_keyword",
        "is_case_sensitive": 0,
        "usage_count": 5,
        "last_used": "2024-01-15 10:30:00"
    }

class TestAddBusinessDialog:
    """Test cases for AddBusinessDialog."""

    def test_initialization(self, qtbot):
        """Test that the dialog initializes correctly."""
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Add Business"
        assert dialog.isModal() is True
        assert dialog.business_name is None

    def test_ui_elements(self, qtbot):
        """Test that all UI elements are present."""
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        
        # Check that key elements exist
        assert hasattr(dialog, 'name_edit')
        assert hasattr(dialog, 'ok_button')
        assert hasattr(dialog, 'cancel_button')
        
        # Check button text
        assert dialog.ok_button.text() == "Add Business"
        assert dialog.cancel_button.text() == "Cancel"

    def test_validation_empty_input(self, qtbot, monkeypatch):
        """Test validation with empty input."""
        # Mock QMessageBox.warning to prevent popup
        mock_warning = MagicMock()
        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)
        
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        
        # Try to accept with empty input
        dialog._on_accept()
        
        # Dialog should not be accepted
        assert dialog.result() != QDialog.DialogCode.Accepted
        assert dialog.business_name is None
        # Verify warning was called
        mock_warning.assert_called_once()

    def test_validation_too_short(self, qtbot, monkeypatch):
        """Test validation with too short input."""
        # Mock QMessageBox.warning to prevent popup
        mock_warning = MagicMock()
        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)
        
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("A")
        
        # Try to accept with short input
        dialog._on_accept()
        
        # Dialog should not be accepted
        assert dialog.result() != QDialog.DialogCode.Accepted
        assert dialog.business_name is None
        # Verify warning was called
        mock_warning.assert_called_once()

    def test_validation_invalid_characters(self, qtbot, monkeypatch):
        """Test validation with invalid characters."""
        # Mock QMessageBox.warning to prevent popup
        mock_warning = MagicMock()
        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)
        
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("Test<Business")
        
        # Try to accept with invalid characters
        dialog._on_accept()
        
        # Dialog should not be accepted
        assert dialog.result() != QDialog.DialogCode.Accepted
        assert dialog.business_name is None
        # Verify warning was called
        mock_warning.assert_called_once()

    def test_valid_input(self, qtbot):
        """Test with valid input."""
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        test_name = "Valid Business Name"
        dialog.name_edit.setText(test_name)
        
        # Accept the dialog
        dialog._on_accept()
        
        # Dialog should be accepted
        assert dialog.result() == QDialog.DialogCode.Accepted
        assert dialog.business_name == test_name

    def test_get_business_name(self, qtbot):
        """Test getting business name."""
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        test_name = "Test Business"
        dialog.business_name = test_name
        
        result = dialog.get_business_name()
        assert result == test_name

    def test_button_states(self, qtbot):
        """Test button enable/disable states."""
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        
        # Initially should be disabled
        assert not dialog.ok_button.isEnabled()
        
        # Enable with text
        dialog.name_edit.setText("Test")
        dialog._on_text_changed()
        assert dialog.ok_button.isEnabled()
        
        # Disable with empty text
        dialog.name_edit.setText("")
        dialog._on_text_changed()
        assert not dialog.ok_button.isEnabled()

    def test_cancel_button(self, qtbot):
        """Test cancel button functionality."""
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("Test Business")
        
        # Click cancel
        qtbot.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)
        
        # Dialog should be rejected
        assert dialog.result() == QDialog.DialogCode.Rejected
        assert dialog.business_name is None

class TestEditKeywordDialog:
    """Test cases for EditKeywordDialog."""

    def test_initialization(self, qtbot, sample_keyword_data):
        """Test that the dialog initializes correctly."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        assert "Edit Keyword - Test Business" in dialog.windowTitle()
        assert dialog.isModal() is True
        assert dialog.edited_keyword is None

    def test_ui_elements(self, qtbot, sample_keyword_data):
        """Test that all UI elements are present."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        
        # Check that key elements exist
        assert hasattr(dialog, 'keyword_edit')
        assert hasattr(dialog, 'case_sensitive_checkbox')
        assert hasattr(dialog, 'save_button')
        assert hasattr(dialog, 'cancel_button')
        assert hasattr(dialog, 'reset_button')

    def test_load_current_data(self, qtbot, sample_keyword_data):
        """Test that current data is loaded correctly."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        
        # Check that data is loaded
        assert dialog.keyword_edit.text() == "test_keyword"
        assert dialog.case_sensitive_checkbox.isChecked() is False  # is_case_sensitive = 0

    def test_load_data_case_sensitive(self, qtbot):
        """Test loading data with case sensitive keyword."""
        keyword_data = {
            "business_name": "Test Business",
            "keyword": "TEST_KEYWORD",
            "is_case_sensitive": 1,
            "usage_count": 3,
            "last_used": "2024-01-16 14:20:00"
        }
        dialog = EditKeywordDialog(keyword_data)
        qtbot.addWidget(dialog)
        
        # Check that data is loaded
        assert dialog.keyword_edit.text() == "TEST_KEYWORD"
        assert dialog.case_sensitive_checkbox.isChecked() is True  # is_case_sensitive = 1

    def test_validation_empty_input(self, qtbot, sample_keyword_data, monkeypatch):
        """Test validation with empty input."""
        # Mock QMessageBox.warning to prevent popup
        mock_warning = MagicMock()
        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)
        
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        dialog.keyword_edit.setText("")
        
        # Try to save with empty input
        dialog._on_save()
        
        # Dialog should not be accepted
        assert dialog.result() != QDialog.DialogCode.Accepted
        assert dialog.edited_keyword is None
        # Verify warning was called
        mock_warning.assert_called_once()

    def test_no_changes(self, qtbot, sample_keyword_data, monkeypatch):
        """Test when no changes are made."""
        # Mock QMessageBox.information to prevent popup
        mock_info = MagicMock()
        monkeypatch.setattr(QMessageBox, 'information', mock_info)
        
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        
        # Try to save without changes
        dialog._on_save()
        
        # Dialog should be rejected (no changes)
        assert dialog.result() == QDialog.DialogCode.Rejected
        assert dialog.edited_keyword is None
        # Verify information was called
        mock_info.assert_called_once()

    def test_valid_changes(self, qtbot, sample_keyword_data):
        """Test with valid changes."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        dialog.keyword_edit.setText("new_keyword")
        dialog.case_sensitive_checkbox.setChecked(True)
        
        # Save changes
        dialog._on_save()
        
        # Dialog should be accepted
        assert dialog.result() == QDialog.DialogCode.Accepted
        assert dialog.edited_keyword == "new_keyword"
        assert dialog.edited_case_sensitive == 1

    def test_get_edited_data(self, qtbot, sample_keyword_data):
        """Test getting edited data."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        dialog.keyword_edit.setText("new_keyword")
        dialog.case_sensitive_checkbox.setChecked(True)
        dialog._on_save()
        
        data = dialog.get_edited_data()
        assert data is not None
        assert data['keyword'] == "new_keyword"
        assert data['is_case_sensitive'] == 1
        assert data['business_name'] == "Test Business"
        assert data['original_keyword'] == "test_keyword"
        assert data['original_case_sensitive'] == 0

    def test_has_changes(self, qtbot, sample_keyword_data):
        """Test has_changes method."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        
        # Initially no changes
        assert not dialog.has_changes()
        
        # Make changes
        dialog.keyword_edit.setText("new_keyword")
        dialog._on_save()
        
        # Should have changes
        assert dialog.has_changes()

    def test_reset_functionality(self, qtbot, sample_keyword_data):
        """Test reset functionality."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        
        # Make changes
        dialog.keyword_edit.setText("new_keyword")
        dialog.case_sensitive_checkbox.setChecked(True)
        
        # Reset
        dialog._on_reset()
        
        # Should be back to original values
        assert dialog.keyword_edit.text() == "test_keyword"
        assert dialog.case_sensitive_checkbox.isChecked() is False

    def test_cancel_button(self, qtbot, sample_keyword_data):
        """Test cancel button functionality."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        dialog.keyword_edit.setText("new_keyword")
        
        # Click cancel
        qtbot.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)
        
        # Dialog should be rejected
        assert dialog.result() == QDialog.DialogCode.Rejected
        assert dialog.edited_keyword is None

    def test_button_states(self, qtbot, sample_keyword_data):
        """Test button enable/disable states."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        
        # Initially should be enabled (has text)
        assert dialog.save_button.isEnabled()
        
        # Disable with empty text
        dialog.keyword_edit.setText("")
        dialog._on_text_changed()
        assert not dialog.save_button.isEnabled()
        
        # Enable with text
        dialog.keyword_edit.setText("Test")
        dialog._on_text_changed()
        assert dialog.save_button.isEnabled()

    def test_usage_display(self, qtbot, sample_keyword_data):
        """Test that usage information is displayed correctly."""
        dialog = EditKeywordDialog(sample_keyword_data)
        qtbot.addWidget(dialog)
        
        # Check usage count
        assert "5 times" in dialog.usage_label.text()
        
        # Check last used
        assert "2024-01-15 10:30:00" in dialog.last_used_label.text()

    def test_usage_display_never_used(self, qtbot):
        """Test usage display for never used keywords."""
        keyword_data = {
            "business_name": "Test Business",
            "keyword": "unused_keyword",
            "is_case_sensitive": 0,
            "usage_count": 0,
            "last_used": None
        }
        dialog = EditKeywordDialog(keyword_data)
        qtbot.addWidget(dialog)
        
        # Check usage count
        assert "0 times" in dialog.usage_label.text()
        
        # Check last used
        assert "Never" in dialog.last_used_label.text() 
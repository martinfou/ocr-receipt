"""
Comprehensive dialog integration tests for projects and categories.

This test file covers:
- Dialog creation and destruction
- Dialog validation integration
- Dialog data flow
- Dialog UI interactions
- Dialog error handling
"""

import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialogButtonBox
from PyQt6.QtCore import Qt
from unittest.mock import Mock, patch

from ocr_receipt.gui.dialogs.add_project_dialog import AddProjectDialog, EditProjectDialog
from ocr_receipt.gui.dialogs.add_category_dialog import AddCategoryDialog, EditCategoryDialog


class TestDialogIntegration:
    """Test dialog integration and functionality."""
    
    def test_project_dialog_creation_and_destruction(self, qtbot):
        """Test that project dialogs can be created and destroyed properly."""
        # Test AddProjectDialog
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        assert dialog.isVisible()
        assert dialog.isModal()
        
        # Test EditProjectDialog
        project_data = {"id": 1, "name": "Test Project", "description": "Test Description"}
        edit_dialog = EditProjectDialog(project_data)
        qtbot.addWidget(edit_dialog)
        assert edit_dialog.isVisible()
        assert edit_dialog.isModal()
        
        # Clean up
        dialog.close()
        edit_dialog.close()
        assert not dialog.isVisible()
        assert not edit_dialog.isVisible()
    
    def test_category_dialog_creation_and_destruction(self, qtbot):
        """Test that category dialogs can be created and destroyed properly."""
        # Test AddCategoryDialog
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        assert dialog.isVisible()
        assert dialog.isModal()
        
        # Test EditCategoryDialog
        category_data = {
            "id": 1, 
            "name": "Test Category", 
            "description": "Test Description",
            "category_code": "TC"
        }
        edit_dialog = EditCategoryDialog(category_data)
        qtbot.addWidget(edit_dialog)
        assert edit_dialog.isVisible()
        assert edit_dialog.isModal()
        
        # Clean up
        dialog.close()
        edit_dialog.close()
        assert not dialog.isVisible()
        assert not edit_dialog.isVisible()
    
    def test_project_dialog_validation_flow(self, qtbot):
        """Test the complete validation flow for project dialogs."""
        # Test AddProjectDialog validation
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        
        # Test empty name validation
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()
        
        # Test short name validation
        dialog.name_edit.setText("A")
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()
        
        # Test valid input
        dialog.name_edit.setText("Valid Project Name")
        dialog.description_edit.setPlainText("Valid description")
        
        # Mock QMessageBox to prevent actual dialog
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_not_called()
            assert dialog.project_name == "Valid Project Name"
            assert dialog.project_description == "Valid description"
    
    def test_category_dialog_validation_flow(self, qtbot):
        """Test the complete validation flow for category dialogs."""
        # Test AddCategoryDialog validation
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        
        # Test empty name validation
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()
        
        # Test short name validation
        dialog.name_edit.setText("A")
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()
        
        # Test valid input
        dialog.name_edit.setText("Valid Category Name")
        dialog.code_edit.setText("VCN")
        dialog.description_edit.setPlainText("Valid description")
        
        # Mock QMessageBox to prevent actual dialog
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_not_called()
            assert dialog.category_name == "Valid Category Name"
            assert dialog.category_code == "VCN"
            assert dialog.category_description == "Valid description"
    
    def test_dialog_button_states(self, qtbot):
        """Test that dialog button states change correctly based on input."""
        # Test project dialog button states
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        
        # Initially, OK button should be disabled
        ok_button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        assert not ok_button.isEnabled()
        
        # After entering text, OK button should be enabled
        dialog.name_edit.setText("Test Project")
        assert ok_button.isEnabled()
        
        # After clearing text, OK button should be disabled again
        dialog.name_edit.clear()
        assert not ok_button.isEnabled()
        
        # Test category dialog button states
        cat_dialog = AddCategoryDialog()
        qtbot.addWidget(cat_dialog)
        
        # Initially, OK button should be disabled
        cat_ok_button = cat_dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        assert not cat_ok_button.isEnabled()
        
        # After entering text, OK button should be enabled
        cat_dialog.name_edit.setText("Test Category")
        assert cat_ok_button.isEnabled()
        
        # After clearing text, OK button should be disabled again
        cat_dialog.name_edit.clear()
        assert not cat_ok_button.isEnabled()
    
    def test_dialog_data_persistence(self, qtbot):
        """Test that dialog data is properly persisted and retrieved."""
        # Test project dialog data persistence
        project_data = {"id": 1, "name": "Original Project", "description": "Original Description"}
        dialog = EditProjectDialog(project_data)
        qtbot.addWidget(dialog)
        
        # Verify initial data is loaded
        assert dialog.name_edit.text() == "Original Project"
        assert dialog.description_edit.toPlainText() == "Original Description"
        
        # Modify data
        dialog.name_edit.setText("Modified Project")
        dialog.description_edit.setPlainText("Modified Description")
        
        # Accept dialog
        dialog._on_accept()
        
        # Verify data is persisted
        assert dialog.get_project_name() == "Modified Project"
        assert dialog.get_project_description() == "Modified Description"
        
        # Test category dialog data persistence
        category_data = {
            "id": 1, 
            "name": "Original Category", 
            "description": "Original Description",
            "category_code": "OC"
        }
        cat_dialog = EditCategoryDialog(category_data)
        qtbot.addWidget(cat_dialog)
        
        # Verify initial data is loaded
        assert cat_dialog.name_edit.text() == "Original Category"
        assert cat_dialog.code_edit.text() == "OC"
        assert cat_dialog.description_edit.toPlainText() == "Original Description"
        
        # Modify data
        cat_dialog.name_edit.setText("Modified Category")
        cat_dialog.code_edit.setText("MC")
        cat_dialog.description_edit.setPlainText("Modified Description")
        
        # Accept dialog
        cat_dialog._on_accept()
        
        # Verify data is persisted
        assert cat_dialog.get_category_name() == "Modified Category"
        assert cat_dialog.get_category_code() == "MC"
        assert cat_dialog.get_category_description() == "Modified Description"
    
    def test_dialog_cancel_functionality(self, qtbot):
        """Test that dialog cancel functionality works correctly."""
        # Test project dialog cancel
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        
        # Enter some data
        dialog.name_edit.setText("Test Project")
        dialog.description_edit.setPlainText("Test Description")
        
        # Click cancel
        cancel_button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Cancel)
        qtbot.mouseClick(cancel_button, Qt.MouseButton.LeftButton)
        
        # Verify dialog is rejected
        assert dialog.result() == dialog.DialogCode.Rejected
        assert not dialog.isVisible()
        
        # Test category dialog cancel
        cat_dialog = AddCategoryDialog()
        qtbot.addWidget(cat_dialog)
        
        # Enter some data
        cat_dialog.name_edit.setText("Test Category")
        cat_dialog.code_edit.setText("TC")
        cat_dialog.description_edit.setPlainText("Test Description")
        
        # Click cancel
        cat_cancel_button = cat_dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Cancel)
        qtbot.mouseClick(cat_cancel_button, Qt.MouseButton.LeftButton)
        
        # Verify dialog is rejected
        assert cat_dialog.result() == cat_dialog.DialogCode.Rejected
        assert not cat_dialog.isVisible()
    
    def test_dialog_error_handling(self, qtbot):
        """Test that dialog error handling works correctly."""
        # Test project dialog with invalid data
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        
        # Test with empty name
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()
            # Verify focus is set to name field
            assert dialog.name_edit.hasFocus()
        
        # Test with short name
        dialog.name_edit.setText("A")
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()
            # Verify focus is set to name field
            assert dialog.name_edit.hasFocus()
        
        # Test category dialog with invalid data
        cat_dialog = AddCategoryDialog()
        qtbot.addWidget(cat_dialog)
        
        # Test with empty name
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            cat_dialog._on_accept()
            mock_warning.assert_called_once()
            # Verify focus is set to name field
            assert cat_dialog.name_edit.hasFocus()
        
        # Test with short name
        cat_dialog.name_edit.setText("A")
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            cat_dialog._on_accept()
            mock_warning.assert_called_once()
            # Verify focus is set to name field
            assert cat_dialog.name_edit.hasFocus()
    
    def test_dialog_ui_consistency(self, qtbot):
        """Test that dialog UI elements are consistent and properly configured."""
        # Test project dialog UI consistency
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        
        # Check that all required elements exist
        assert hasattr(dialog, 'name_edit')
        assert hasattr(dialog, 'description_edit')
        assert dialog.name_edit is not None
        assert dialog.description_edit is not None
        
        # Check that placeholders are set
        assert dialog.name_edit.placeholderText() != ""
        assert dialog.description_edit.placeholderText() != ""
        
        # Check that max lengths are set
        assert dialog.name_edit.maxLength() > 0
        
        # Test category dialog UI consistency
        cat_dialog = AddCategoryDialog()
        qtbot.addWidget(cat_dialog)
        
        # Check that all required elements exist
        assert hasattr(cat_dialog, 'name_edit')
        assert hasattr(cat_dialog, 'code_edit')
        assert hasattr(cat_dialog, 'description_edit')
        assert cat_dialog.name_edit is not None
        assert cat_dialog.code_edit is not None
        assert cat_dialog.description_edit is not None
        
        # Check that placeholders are set
        assert cat_dialog.name_edit.placeholderText() != ""
        assert cat_dialog.code_edit.placeholderText() != ""
        assert cat_dialog.description_edit.placeholderText() != ""
        
        # Check that max lengths are set
        assert cat_dialog.name_edit.maxLength() > 0
        assert cat_dialog.code_edit.maxLength() > 0 
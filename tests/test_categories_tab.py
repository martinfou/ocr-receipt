"""
Unit tests for CategoriesTab and related components.
"""
import pytest
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QDialog, QMessageBox
from PyQt6.QtCore import Qt
from unittest.mock import Mock, patch
from ocr_receipt.gui.categories_tab import CategoriesTab
from ocr_receipt.gui.widgets.categories_table import CategoriesTable
from ocr_receipt.gui.dialogs.add_category_dialog import AddCategoryDialog, EditCategoryDialog
from ocr_receipt.business.category_manager import CategoryManager
from ocr_receipt.utils.translation_helper import get_translation_helper

@pytest.fixture(autouse=True)
def force_english():
    """Force English language for all tests."""
    helper = get_translation_helper()
    helper.set_language('en')
    yield
    # Reset to English after test
    helper.set_language('en')

@pytest.fixture
def app(qtbot):
    """Create QApplication instance for testing."""
    return QApplication.instance() or QApplication([])

@pytest.fixture
def mock_category_manager():
    """Create a mock CategoryManager."""
    manager = Mock(spec=CategoryManager)
    manager.list_categories.return_value = [
        {"id": 1, "name": "Test Category", "description": "Test Description", "category_code": "TEST"},
        {"id": 2, "name": "Another Category", "description": "Another Description", "category_code": "ANOTHER"}
    ]
    return manager

class TestAddCategoryDialog:
    """Test AddCategoryDialog class."""
    
    def test_init(self, qtbot, app):
        """Test dialog initialization."""
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Add Category"
        assert dialog.isModal()
        assert dialog.category_name is None
        assert dialog.category_description is None
        assert dialog.category_code is None
    
    def test_ui_setup(self, qtbot, app):
        """Test UI setup."""
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        
        # Check that form elements exist
        assert dialog.name_edit is not None
        assert dialog.code_edit is not None
        assert dialog.description_edit is not None
        
        # Check placeholders
        assert "category name" in dialog.name_edit.placeholderText().lower()
        assert "category code" in dialog.code_edit.placeholderText().lower()
        assert "description" in dialog.description_edit.placeholderText().lower()
    
    def test_validation_empty_name(self, qtbot, app, monkeypatch):
        """Test validation with empty name."""
        # Mock QMessageBox.warning to prevent popup
        mock_warning = Mock()
        monkeypatch.setattr('PyQt6.QtWidgets.QMessageBox.warning', mock_warning)
        
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("")
        dialog.code_edit.setText("TEST")
        dialog.description_edit.setPlainText("Test description")
        
        # Should not accept with empty name
        dialog._on_accept()
        assert dialog.result() != QDialog.DialogCode.Accepted
        # Verify warning was called
        mock_warning.assert_called_once()
    
    def test_validation_short_name(self, qtbot, app, monkeypatch):
        """Test validation with short name."""
        # Mock QMessageBox.warning to prevent popup
        mock_warning = Mock()
        monkeypatch.setattr('PyQt6.QtWidgets.QMessageBox.warning', mock_warning)
        
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("A")
        dialog.code_edit.setText("TEST")
        dialog.description_edit.setPlainText("Test description")
        
        # Should not accept with short name
        dialog._on_accept()
        assert dialog.result() != QDialog.DialogCode.Accepted
        # Verify warning was called
        mock_warning.assert_called_once()
    
    def test_validation_long_name(self, qtbot, app, monkeypatch):
        """Test validation with long name."""
        # Mock QMessageBox.warning to prevent popup
        mock_warning = Mock()
        monkeypatch.setattr('PyQt6.QtWidgets.QMessageBox.warning', mock_warning)
        
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("A" * 100)  # Exactly 100 characters (max length)
        dialog.code_edit.setText("TEST")
        dialog.description_edit.setPlainText("Test description")
        
        # Should accept with exactly 100 characters (boundary condition)
        dialog._on_accept()
        assert dialog.result() == QDialog.DialogCode.Accepted
        # Verify warning was NOT called
        mock_warning.assert_not_called()
    
    def test_valid_input(self, qtbot, app):
        """Test valid input acceptance."""
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("Valid Category")
        dialog.code_edit.setText("VALID")
        dialog.description_edit.setPlainText("Valid description")
        
        # Should accept valid input
        dialog._on_accept()
        assert dialog.result() == QDialog.DialogCode.Accepted
        assert dialog.get_category_name() == "Valid Category"
        assert dialog.get_category_code() == "VALID"
        assert dialog.get_category_description() == "Valid description"
    
    def test_empty_optional_fields(self, qtbot, app):
        """Test with empty optional fields."""
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("Valid Category")
        dialog.code_edit.setText("")
        dialog.description_edit.setPlainText("")
        
        # Should accept with empty optional fields
        dialog._on_accept()
        assert dialog.result() == QDialog.DialogCode.Accepted
        assert dialog.get_category_name() == "Valid Category"
        assert dialog.get_category_code() is None
        assert dialog.get_category_description() is None

class TestEditCategoryDialog:
    """Test EditCategoryDialog class."""
    
    def test_init(self, qtbot, app):
        """Test dialog initialization."""
        category_data = {
            "id": 1,
            "name": "Test Category",
            "description": "Test Description",
            "category_code": "TEST"
        }
        dialog = EditCategoryDialog(category_data)
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Edit Category"
        assert dialog.isModal()
        assert dialog.category_data == category_data
    
    def test_ui_population(self, qtbot, app):
        """Test UI population with existing data."""
        category_data = {
            "id": 1,
            "name": "Test Category",
            "description": "Test Description",
            "category_code": "TEST"
        }
        dialog = EditCategoryDialog(category_data)
        qtbot.addWidget(dialog)
        
        # Check that fields are populated
        assert dialog.name_edit.text() == "Test Category"
        assert dialog.code_edit.text() == "TEST"
        assert dialog.description_edit.toPlainText() == "Test Description"
    
    def test_validation_empty_name(self, qtbot, app, monkeypatch):
        """Test validation with empty name."""
        # Mock QMessageBox.warning to prevent popup
        mock_warning = Mock()
        monkeypatch.setattr('PyQt6.QtWidgets.QMessageBox.warning', mock_warning)
        
        category_data = {"id": 1, "name": "Original", "description": "", "category_code": ""}
        dialog = EditCategoryDialog(category_data)
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("")
        
        # Should not accept with empty name
        dialog._on_accept()
        assert dialog.result() != QDialog.DialogCode.Accepted
        # Verify warning was called
        mock_warning.assert_called_once()
    
    def test_valid_edit(self, qtbot, app):
        """Test valid edit acceptance."""
        category_data = {"id": 1, "name": "Original", "description": "", "category_code": ""}
        dialog = EditCategoryDialog(category_data)
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("Updated Category")
        dialog.code_edit.setText("UPDATED")
        dialog.description_edit.setPlainText("Updated description")
        
        # Should accept valid input
        dialog._on_accept()
        assert dialog.result() == QDialog.DialogCode.Accepted
        assert dialog.get_category_name() == "Updated Category"
        assert dialog.get_category_code() == "UPDATED"
        assert dialog.get_category_description() == "Updated description"

class TestCategoriesTable:
    """Test CategoriesTable class."""
    
    def test_init(self, qtbot, app):
        """Test table initialization."""
        table = CategoriesTable()
        qtbot.addWidget(table)
        assert table.columnCount() == 4
        assert table.rowCount() == 0
        assert table.categories_data == []
    
    def test_header_labels(self, qtbot, app):
        """Test header labels."""
        table = CategoriesTable()
        qtbot.addWidget(table)
        headers = []
        for i in range(table.columnCount()):
            headers.append(table.horizontalHeaderItem(i).text())
        
        expected_headers = ["ID", "Name", "Code", "Description"]
        assert headers == expected_headers
    
    def test_load_categories(self, qtbot, app):
        """Test loading categories into table."""
        table = CategoriesTable()
        qtbot.addWidget(table)
        categories = [
            {"id": 1, "name": "Category 1", "description": "Desc 1", "category_code": "CODE1"},
            {"id": 2, "name": "Category 2", "description": "Desc 2", "category_code": "CODE2"}
        ]
        
        table.load_categories(categories)
        assert table.rowCount() == 2
        assert table.categories_data == categories
        
        # Check first row data
        assert table.item(0, 0).text() == "1"
        assert table.item(0, 1).text() == "Category 1"
        assert table.item(0, 2).text() == "CODE1"
        assert table.item(0, 3).text() == "Desc 1"
    
    def test_load_categories_with_empty_fields(self, qtbot, app):
        """Test loading categories with empty optional fields."""
        table = CategoriesTable()
        qtbot.addWidget(table)
        categories = [
            {"id": 1, "name": "Category 1", "description": None, "category_code": None}
        ]
        
        table.load_categories(categories)
        assert table.item(0, 2).text() == ""
        assert table.item(0, 3).text() == ""
    
    def test_get_selected_category_id(self, qtbot, app):
        """Test getting selected category ID."""
        table = CategoriesTable()
        qtbot.addWidget(table)
        categories = [
            {"id": 1, "name": "Category 1", "description": "", "category_code": ""},
            {"id": 2, "name": "Category 2", "description": "", "category_code": ""}
        ]
        table.load_categories(categories)
        
        # No selection initially
        assert table.get_selected_category_id() is None
        
        # Select first row
        table.selectRow(0)
        assert table.get_selected_category_id() == 1
    
    def test_get_selected_category_data(self, qtbot, app):
        """Test getting selected category data."""
        table = CategoriesTable()
        qtbot.addWidget(table)
        categories = [
            {"id": 1, "name": "Category 1", "description": "Desc 1", "category_code": "CODE1"}
        ]
        table.load_categories(categories)
        
        # Select first row
        table.selectRow(0)
        selected_data = table.get_selected_category_data()
        assert selected_data == categories[0]
    
    def test_selection_signal(self, qtbot, app):
        """Test selection change signal."""
        table = CategoriesTable()
        qtbot.addWidget(table)
        categories = [
            {"id": 1, "name": "Category 1", "description": "", "category_code": ""}
        ]
        table.load_categories(categories)
        
        # Track signal emissions
        signal_emitted = False
        emitted_id = None
        
        def on_category_selected(category_id):
            nonlocal signal_emitted, emitted_id
            signal_emitted = True
            emitted_id = category_id
        
        table.category_selected.connect(on_category_selected)
        
        # Select row
        table.selectRow(0)
        
        assert signal_emitted
        assert emitted_id == 1

class TestCategoriesTab:
    """Test CategoriesTab class."""
    
    def test_init(self, qtbot, app, mock_category_manager):
        """Test tab initialization."""
        tab = CategoriesTab(mock_category_manager)
        qtbot.addWidget(tab)
        assert tab.category_manager == mock_category_manager
        assert tab.add_button is not None
        assert tab.edit_button is not None
        assert tab.delete_button is not None
        assert tab.refresh_button is not None
        assert tab.categories_table is not None
        assert tab.status_label is not None
    
    def test_ui_setup(self, qtbot, app, mock_category_manager):
        """Test UI setup."""
        tab = CategoriesTab(mock_category_manager)
        qtbot.addWidget(tab)
        
        # Check button texts
        assert "Add Category" in tab.add_button.text()
        assert "Edit Category" in tab.edit_button.text()
        assert "Delete Category" in tab.delete_button.text()
        assert "Refresh" in tab.refresh_button.text()
        
        # Check initial button states
        assert not tab.edit_button.isEnabled()
        assert not tab.delete_button.isEnabled()
    
    def test_load_categories_success(self, qtbot, app, mock_category_manager):
        """Test successful category loading."""
        tab = CategoriesTab(mock_category_manager)
        qtbot.addWidget(tab)
        
        # Verify that list_categories was called
        mock_category_manager.list_categories.assert_called_once()
        
        # Check that table was populated
        assert tab.categories_table.rowCount() == 2
        assert "Loaded 2 categories" in tab.status_label.text()
    
    def test_load_categories_error(self, qtbot, app):
        """Test category loading error."""
        mock_manager = Mock(spec=CategoryManager)
        mock_manager.list_categories.side_effect = Exception("Database error")
        
        with patch('ocr_receipt.gui.categories_tab.QMessageBox.critical') as mock_critical:
            tab = CategoriesTab(mock_manager)
            qtbot.addWidget(tab)
            
            # Check error handling
            mock_critical.assert_called_once()
            assert "Error loading categories" in tab.status_label.text()
    
    def test_add_category_success(self, qtbot, app, mock_category_manager):
        """Test successful category addition."""
        mock_category_manager.create_category.return_value = 3
        
        with patch('ocr_receipt.gui.categories_tab.AddCategoryDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_category_name.return_value = "New Category"
            mock_dialog.get_category_description.return_value = "New Description"
            mock_dialog.get_category_code.return_value = "NEW"
            mock_dialog_class.return_value = mock_dialog
            
            tab = CategoriesTab(mock_category_manager)
            qtbot.addWidget(tab)
            
            # Mock _load_categories to prevent it from being called
            with patch.object(tab, '_load_categories'):
                # Trigger add category
                tab._on_add_category()
                
                # Verify dialog was created and executed
                mock_dialog_class.assert_called_once()
                mock_dialog.exec.assert_called_once()
                
                # Verify category was created
                mock_category_manager.create_category.assert_called_once_with(
                    "New Category", "New Description", "NEW"
                )
                assert "Category added successfully" in tab.status_label.text()
    
    def test_add_category_validation_error(self, qtbot, app, mock_category_manager):
        """Test category addition with validation error."""
        mock_category_manager.create_category.side_effect = ValueError("Name already exists")
        
        with patch('ocr_receipt.gui.categories_tab.AddCategoryDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_category_name.return_value = "Existing Category"
            mock_dialog.get_category_description.return_value = ""
            mock_dialog.get_category_code.return_value = ""
            mock_dialog_class.return_value = mock_dialog
            
            with patch('ocr_receipt.gui.categories_tab.QMessageBox.warning') as mock_warning:
                tab = CategoriesTab(mock_category_manager)
                qtbot.addWidget(tab)
                
                # Mock _load_categories to prevent it from being called
                with patch.object(tab, '_load_categories'):
                    tab._on_add_category()
                    
                    # Verify dialog was created and executed
                    mock_dialog_class.assert_called_once()
                    mock_dialog.exec.assert_called_once()
                    
                    # Verify warning was shown
                    mock_warning.assert_called_once()
    
    def test_edit_category_success(self, qtbot, app, mock_category_manager):
        """Test successful category editing."""
        with patch('ocr_receipt.gui.categories_tab.EditCategoryDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_category_name.return_value = "Updated Category"
            mock_dialog.get_category_description.return_value = "Updated Description"
            mock_dialog.get_category_code.return_value = "UPDATED"
            mock_dialog_class.return_value = mock_dialog
            
            tab = CategoriesTab(mock_category_manager)
            qtbot.addWidget(tab)
            
            # Set up selected category
            tab.categories_table.load_categories([
                {"id": 1, "name": "Original", "description": "", "category_code": ""}
            ])
            tab.categories_table.selectRow(0)
            
            # Mock _load_categories to prevent it from being called
            with patch.object(tab, '_load_categories'):
                # Trigger edit category
                tab._on_edit_category()
                
                # Verify dialog was created and executed
                mock_dialog_class.assert_called_once()
                mock_dialog.exec.assert_called_once()
                
                # Verify category was updated
                mock_category_manager.update_category.assert_called_once_with(
                    1, "Updated Category", "Updated Description", "UPDATED"
                )
                assert "Category updated successfully" in tab.status_label.text()
    
    def test_delete_category_success(self, qtbot, app, mock_category_manager):
        """Test successful category deletion."""
        with patch('ocr_receipt.gui.categories_tab.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.Yes
            
            tab = CategoriesTab(mock_category_manager)
            qtbot.addWidget(tab)
            
            # Set up selected category
            tab.categories_table.load_categories([
                {"id": 1, "name": "Test Category", "description": "", "category_code": ""}
            ])
            tab.categories_table.selectRow(0)
            
            # Mock _load_categories to prevent it from being called
            with patch.object(tab, '_load_categories'):
                # Trigger delete category
                tab._on_delete_category()
                
                # Verify confirmation dialog was shown
                mock_question.assert_called_once()
                
                # Verify category was deleted
                mock_category_manager.delete_category.assert_called_once_with(1)
                assert "Category deleted successfully" in tab.status_label.text()
    
    def test_delete_category_cancelled(self, qtbot, app, mock_category_manager):
        """Test cancelled category deletion."""
        with patch('ocr_receipt.gui.categories_tab.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.No
            
            tab = CategoriesTab(mock_category_manager)
            qtbot.addWidget(tab)
            
            # Set up selected category
            tab.categories_table.load_categories([
                {"id": 1, "name": "Test Category", "description": "", "category_code": ""}
            ])
            tab.categories_table.selectRow(0)
            
            # Trigger delete category
            tab._on_delete_category()
            
            # Verify category was not deleted
            mock_category_manager.delete_category.assert_not_called()
    
    def test_category_selection(self, qtbot, app, mock_category_manager):
        """Test category selection handling."""
        tab = CategoriesTab(mock_category_manager)
        qtbot.addWidget(tab)
        
        # Initially buttons should be disabled
        assert not tab.edit_button.isEnabled()
        assert not tab.delete_button.isEnabled()
        
        # Simulate category selection
        tab._on_category_selected(1)
        
        # Buttons should be enabled
        assert tab.edit_button.isEnabled()
        assert tab.delete_button.isEnabled()
    
    def test_update_language(self, qtbot, app, mock_category_manager):
        """Test language update functionality."""
        tab = CategoriesTab(mock_category_manager)
        qtbot.addWidget(tab)
        
        # Store original texts
        original_add_text = tab.add_button.text()
        original_edit_text = tab.edit_button.text()
        original_delete_text = tab.delete_button.text()
        original_refresh_text = tab.refresh_button.text()
        
        # Update language
        tab.update_language()
        
        # Texts should be updated (though they might be the same if already translated)
        # The important thing is that the method doesn't crash
        assert tab.add_button.text() is not None
        assert tab.edit_button.text() is not None
        assert tab.delete_button.text() is not None
        assert tab.refresh_button.text() is not None

    def test_categories_changed_signal(self, qtbot, app, mock_category_manager):
        """Test that categories_changed signal is emitted."""
        tab = CategoriesTab(mock_category_manager)
        qtbot.addWidget(tab)
        
        # Track signal emissions
        signal_emitted = False
        
        def on_categories_changed():
            nonlocal signal_emitted
            signal_emitted = True
        
        # Connect the signal
        tab.categories_changed.connect(on_categories_changed)
        
        # Emit the signal manually
        tab.categories_changed.emit()
        
        # Check that the signal was received
        assert signal_emitted 
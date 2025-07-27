"""
Integration tests for Projects and Categories tabs.

This test file covers:
- End-to-end workflows between projects and categories tabs
- Data consistency across tab operations
- Integration between dialogs and tables
- Cross-tab data sharing and validation
"""

import pytest
import tempfile
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialogButtonBox, QWidget
from PyQt6.QtCore import Qt
from unittest.mock import Mock, patch

from ocr_receipt.gui.projects_tab import ProjectsTab
from ocr_receipt.gui.categories_tab import CategoriesTab
from ocr_receipt.gui.widgets.projects_table import ProjectsTable
from ocr_receipt.gui.widgets.categories_table import CategoriesTable
from ocr_receipt.gui.dialogs.add_project_dialog import AddProjectDialog, EditProjectDialog
from ocr_receipt.gui.dialogs.add_category_dialog import AddCategoryDialog, EditCategoryDialog
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.project_manager import ProjectManager
from ocr_receipt.business.category_manager import CategoryManager


class TestProjectsCategoriesIntegration:
    """Test integration between projects and categories tabs."""
    
    @pytest.fixture
    def setup_managers(self):
        """Set up database and managers for testing."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            db_manager.initialize_database()
            project_manager = ProjectManager(db_manager)
            category_manager = CategoryManager(db_manager)
            
            yield db_manager, project_manager, category_manager
            
        finally:
            db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass
    
    @pytest.fixture
    def projects_tab(self, qtbot, setup_managers):
        """Create a ProjectsTab for testing."""
        db_manager, project_manager, category_manager = setup_managers
        tab = ProjectsTab(project_manager)
        qtbot.addWidget(tab)
        return tab, project_manager
    
    @pytest.fixture
    def categories_tab(self, qtbot, setup_managers):
        """Create a CategoriesTab for testing."""
        db_manager, project_manager, category_manager = setup_managers
        tab = CategoriesTab(category_manager)
        qtbot.addWidget(tab)
        return tab, category_manager
    
    def test_project_creation_workflow(self, projects_tab, qtbot):
        """Test complete workflow of creating a project through the tab."""
        tab, project_manager = projects_tab
        
        # Get initial state
        initial_count = tab.projects_table.rowCount()
        
        # Create dialog and add project
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        
        # Enter project details
        qtbot.keyClicks(dialog.name_edit, "Test Integration Project")
        qtbot.keyClicks(dialog.description_edit, "This is a test project for integration testing")
        qtbot.wait(100)
        
        # Accept the dialog
        button_box = dialog.findChild(QDialogButtonBox)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        
        # Verify dialog is closed and accepted
        assert not dialog.isVisible()
        assert dialog.result() == dialog.DialogCode.Accepted
        
        # Get the project details from dialog
        project_name = dialog.get_project_name()
        project_description = dialog.get_project_description()
        assert project_name == "Test Integration Project"
        assert project_description == "This is a test project for integration testing"
        
        # Add the project to the database
        project_id = project_manager.create_project(project_name, project_description)
        assert project_id is not None
        
        # Refresh the tab
        tab._load_projects()
        
        # Verify the project appears in the table
        table = tab.projects_table
        assert table.rowCount() == initial_count + 1
        
        # Find the new project in the table
        found = False
        for row in range(table.rowCount()):
            if (table.item(row, 0) and 
                table.item(row, 0).text() == project_name):
                found = True
                break
        
        assert found, "New project should appear in the projects table"
    
    def test_category_creation_workflow(self, categories_tab, qtbot):
        """Test complete workflow of creating a category through the tab."""
        tab, category_manager = categories_tab
        
        # Get initial state
        initial_count = tab.categories_table.rowCount()
        
        # Create dialog and add category
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        
        # Enter category details
        qtbot.keyClicks(dialog.name_edit, "Test Integration Category")
        qtbot.keyClicks(dialog.code_edit, "TIC")
        qtbot.keyClicks(dialog.description_edit, "This is a test category for integration testing")
        qtbot.wait(100)
        
        # Accept the dialog
        button_box = dialog.findChild(QDialogButtonBox)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        
        # Verify dialog is closed and accepted
        assert not dialog.isVisible()
        assert dialog.result() == dialog.DialogCode.Accepted
        
        # Get the category details from dialog
        category_name = dialog.get_category_name()
        category_code = dialog.get_category_code()
        category_description = dialog.get_category_description()
        assert category_name == "Test Integration Category"
        assert category_code == "TIC"
        assert category_description == "This is a test category for integration testing"
        
        # Add the category to the database
        category_id = category_manager.create_category(category_name, category_description, category_code)
        assert category_id is not None
        
        # Refresh the tab
        tab._load_categories()
        
        # Verify the category appears in the table
        table = tab.categories_table
        assert table.rowCount() == initial_count + 1
        
        # Find the new category in the table
        found = False
        for row in range(table.rowCount()):
            if (table.item(row, 1) and 
                table.item(row, 1).text() == category_name):
                found = True
                break
        
        assert found, "New category should appear in the categories table"
    
    def test_project_edit_workflow(self, projects_tab, qtbot):
        """Test complete workflow of editing a project through the tab."""
        tab, project_manager = projects_tab
        
        # First create a project
        project_id = project_manager.create_project("Original Project", "Original description")
        assert project_id is not None
        
        # Refresh the tab
        tab._load_projects()
        
        # Select the project in the table
        table = tab.projects_table
        table.selectRow(0)
        qtbot.wait(100)
        
        # Verify edit button is enabled
        assert tab.edit_button.isEnabled()
        
        # Click edit button
        qtbot.mouseClick(tab.edit_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        
        # The edit dialog should be created by the tab's edit button click
        # We need to wait for it to be created and then find it
        qtbot.wait(100)
        
        # Find the edit dialog among all widgets
        edit_dialogs = []
        def find_edit_dialogs(widget):
            if isinstance(widget, EditProjectDialog):
                edit_dialogs.append(widget)
            for child in widget.findChildren(QWidget):
                find_edit_dialogs(child)
        
        find_edit_dialogs(QApplication.instance())
        assert len(edit_dialogs) == 1
        dialog = edit_dialogs[0]
        
        # Modify the project details
        dialog.name_edit.clear()
        qtbot.keyClicks(dialog.name_edit, "Updated Project")
        dialog.description_edit.clear()
        qtbot.keyClicks(dialog.description_edit, "Updated description")
        qtbot.wait(100)
        
        # Accept the dialog
        button_box = dialog.findChild(QDialogButtonBox)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        
        # Verify the project was updated
        updated_project = project_manager.get_project_by_id(project_id)
        assert updated_project['name'] == "Updated Project"
        assert updated_project['description'] == "Updated description"
    
    def test_category_edit_workflow(self, categories_tab, qtbot):
        """Test complete workflow of editing a category through the tab."""
        tab, category_manager = categories_tab
        
        # First create a category
        category_id = category_manager.create_category("Original Category", "Original description", "OC")
        assert category_id is not None
        
        # Refresh the tab
        tab._load_categories()
        
        # Select the category in the table
        table = tab.categories_table
        table.selectRow(0)
        qtbot.wait(100)
        
        # Verify edit button is enabled
        assert tab.edit_button.isEnabled()
        
        # Click edit button
        qtbot.mouseClick(tab.edit_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        
        # The edit dialog should be created by the tab's edit button click
        # We need to wait for it to be created and then find it
        qtbot.wait(100)
        
        # Find the edit dialog among all widgets
        edit_dialogs = []
        def find_edit_dialogs(widget):
            if isinstance(widget, EditCategoryDialog):
                edit_dialogs.append(widget)
            for child in widget.findChildren(QWidget):
                find_edit_dialogs(child)
        
        find_edit_dialogs(QApplication.instance())
        assert len(edit_dialogs) == 1
        dialog = edit_dialogs[0]
        
        # Modify the category details
        dialog.name_edit.clear()
        qtbot.keyClicks(dialog.name_edit, "Updated Category")
        dialog.code_edit.clear()
        qtbot.keyClicks(dialog.code_edit, "UC")
        dialog.description_edit.clear()
        qtbot.keyClicks(dialog.description_edit, "Updated description")
        qtbot.wait(100)
        
        # Accept the dialog
        button_box = dialog.findChild(QDialogButtonBox)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        
        # Verify the category was updated
        updated_category = category_manager.get_category_by_id(category_id)
        assert updated_category['name'] == "Updated Category"
        assert updated_category['category_code'] == "UC"
        assert updated_category['description'] == "Updated description"
    
    def test_project_delete_workflow(self, projects_tab, qtbot):
        """Test complete workflow of deleting a project through the tab."""
        tab, project_manager = projects_tab
        
        # First create a project
        project_id = project_manager.create_project("Project to Delete", "Will be deleted")
        assert project_id is not None
        
        # Refresh the tab
        tab._load_projects()
        initial_count = tab.projects_table.rowCount()
        
        # Select the project in the table
        table = tab.projects_table
        table.selectRow(0)
        qtbot.wait(100)
        
        # Verify delete button is enabled
        assert tab.delete_button.isEnabled()
        
        # Mock QMessageBox.question to return Yes
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.Yes
            
            # Click delete button
            qtbot.mouseClick(tab.delete_button, Qt.MouseButton.LeftButton)
            qtbot.wait(100)
        
        # Verify the project was deleted
        assert tab.projects_table.rowCount() == initial_count - 1
        
        # Verify project no longer exists in database
        assert project_manager.get_project_by_id(project_id) is None
    
    def test_category_delete_workflow(self, categories_tab, qtbot):
        """Test complete workflow of deleting a category through the tab."""
        tab, category_manager = categories_tab
        
        # First create a category
        category_id = category_manager.create_category("Category to Delete", "Will be deleted", "CTD")
        assert category_id is not None
        
        # Refresh the tab
        tab._load_categories()
        initial_count = tab.categories_table.rowCount()
        
        # Select the category in the table
        table = tab.categories_table
        table.selectRow(0)
        qtbot.wait(100)
        
        # Verify delete button is enabled
        assert tab.delete_button.isEnabled()
        
        # Mock QMessageBox.question to return Yes
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.Yes
            
            # Click delete button
            qtbot.mouseClick(tab.delete_button, Qt.MouseButton.LeftButton)
            qtbot.wait(100)
        
        # Verify the category was deleted
        assert tab.categories_table.rowCount() == initial_count - 1
        
        # Verify category no longer exists in database
        assert category_manager.get_category_by_id(category_id) is None
    
    def test_table_selection_signals(self, projects_tab, categories_tab, qtbot):
        """Test that table selection signals work correctly."""
        projects_tab_instance, project_manager = projects_tab
        categories_tab_instance, category_manager = categories_tab
        
        # Create test data
        project_id = project_manager.create_project("Test Project", "Test description")
        category_id = category_manager.create_category("Test Category", "Test description", "TC")
        
        # Load data into tabs
        projects_tab_instance._load_projects()
        categories_tab_instance._load_categories()
        
        # Test project table selection
        project_selected = False
        def on_project_selected(pid):
            nonlocal project_selected
            project_selected = True
            assert pid == project_id
        
        projects_tab_instance.projects_table.project_selected.connect(on_project_selected)
        projects_tab_instance.projects_table.selectRow(0)
        qtbot.wait(100)
        
        assert project_selected, "Project selection signal should be emitted"
        
        # Test category table selection
        category_selected = False
        def on_category_selected(cid):
            nonlocal category_selected
            category_selected = True
            assert cid == category_id
        
        categories_tab_instance.categories_table.category_selected.connect(on_category_selected)
        categories_tab_instance.categories_table.selectRow(0)
        qtbot.wait(100)
        
        assert category_selected, "Category selection signal should be emitted"
    
    def test_dialog_validation_integration(self, qtbot):
        """Test that dialog validation works correctly in integration scenarios."""
        # Test project dialog validation
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        
        # Try to accept with invalid data
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()
        
        # Test category dialog validation
        dialog = AddCategoryDialog()
        qtbot.addWidget(dialog)
        
        # Try to accept with invalid data
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()
    
    def test_tab_refresh_integration(self, projects_tab, categories_tab, qtbot):
        """Test that tab refresh functionality works correctly."""
        projects_tab_instance, project_manager = projects_tab
        categories_tab_instance, category_manager = categories_tab
        
        # Create initial data
        project_manager.create_project("Project 1", "Description 1")
        category_manager.create_category("Category 1", "Description 1", "C1")
        
        # Load data
        projects_tab_instance._load_projects()
        categories_tab_instance._load_categories()
        
        initial_project_count = projects_tab_instance.projects_table.rowCount()
        initial_category_count = categories_tab_instance.categories_table.rowCount()
        
        # Add more data directly to managers
        project_manager.create_project("Project 2", "Description 2")
        category_manager.create_category("Category 2", "Description 2", "C2")
        
        # Refresh tabs
        qtbot.mouseClick(projects_tab_instance.refresh_button, Qt.MouseButton.LeftButton)
        qtbot.mouseClick(categories_tab_instance.refresh_button, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        
        # Verify new data appears
        assert projects_tab_instance.projects_table.rowCount() == initial_project_count + 1
        assert categories_tab_instance.categories_table.rowCount() == initial_category_count + 1 
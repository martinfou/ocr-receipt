"""
Tests for ProjectsTab and related components.
"""
import pytest
from PyQt6.QtWidgets import QApplication, QTableWidgetItem
from PyQt6.QtCore import Qt
from unittest.mock import Mock, patch, MagicMock
from src.ocr_receipt.gui.projects_tab import (
    ProjectsTab, ProjectsTable, AddProjectDialog, EditProjectDialog
)
from src.ocr_receipt.business.project_manager import ProjectManager
from src.ocr_receipt.business.database_manager import DatabaseManager

@pytest.fixture
def app():
    """Create QApplication instance for testing."""
    return QApplication([])

@pytest.fixture
def mock_db_manager():
    """Create a mock database manager."""
    return Mock(spec=DatabaseManager)

@pytest.fixture
def mock_project_manager(mock_db_manager):
    """Create a mock project manager."""
    return Mock(spec=ProjectManager)

@pytest.fixture
def sample_projects():
    """Sample project data for testing."""
    return [
        {"id": 1, "name": "Project Alpha", "description": "First project"},
        {"id": 2, "name": "Project Beta", "description": "Second project"},
        {"id": 3, "name": "Project Gamma", "description": None}
    ]

class TestAddProjectDialog:
    """Test AddProjectDialog functionality."""
    
    def test_init(self, app):
        """Test dialog initialization."""
        dialog = AddProjectDialog()
        assert dialog.windowTitle() == "Add Project"
        assert dialog.isModal()
        assert dialog.project_name is None
        assert dialog.project_description is None

    def test_ui_setup(self, app):
        """Test UI components are properly set up."""
        dialog = AddProjectDialog()
        
        # Check that form fields exist
        assert dialog.name_edit is not None
        assert dialog.description_edit is not None
        
        # Check placeholders
        assert "Enter project name" in dialog.name_edit.placeholderText()
        assert "Enter project description" in dialog.description_edit.placeholderText()

    def test_validation_empty_name(self, app):
        """Test validation with empty name."""
        dialog = AddProjectDialog()
        dialog.name_edit.setText("")
        
        # Mock QMessageBox to capture warning
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()

    def test_validation_short_name(self, app):
        """Test validation with short name."""
        dialog = AddProjectDialog()
        dialog.name_edit.setText("A")
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()

    def test_validation_long_name(self, app):
        """Test validation with long name."""
        dialog = AddProjectDialog()
        dialog.name_edit.setText("A" * 101)  # 101 characters
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()

    def test_valid_input(self, app):
        """Test valid input acceptance."""
        dialog = AddProjectDialog()
        dialog.name_edit.setText("Valid Project")
        dialog.description_edit.setPlainText("Valid description")
        
        with patch.object(dialog, 'accept') as mock_accept:
            dialog._on_accept()
            mock_accept.assert_called_once()
            assert dialog.project_name == "Valid Project"
            assert dialog.project_description == "Valid description"

    def test_empty_description(self, app):
        """Test handling of empty description."""
        dialog = AddProjectDialog()
        dialog.name_edit.setText("Valid Project")
        dialog.description_edit.setPlainText("")
        
        with patch.object(dialog, 'accept') as mock_accept:
            dialog._on_accept()
            mock_accept.assert_called_once()
            assert dialog.project_name == "Valid Project"
            assert dialog.project_description is None

    def test_button_state_changes(self, app):
        """Test OK button state changes with text input."""
        dialog = AddProjectDialog()
        ok_button = dialog.findChild(dialog.findChild.__class__).button(dialog.findChild.__class__.StandardButton.Ok)
        
        # Initially disabled
        assert not ok_button.isEnabled()
        
        # Enable with text
        dialog.name_edit.setText("Test")
        assert ok_button.isEnabled()
        
        # Disable with empty text
        dialog.name_edit.setText("")
        assert not ok_button.isEnabled()

class TestEditProjectDialog:
    """Test EditProjectDialog functionality."""
    
    def test_init_with_project_data(self, app):
        """Test dialog initialization with project data."""
        project_data = {"id": 1, "name": "Test Project", "description": "Test Description"}
        dialog = EditProjectDialog(project_data)
        
        assert dialog.windowTitle() == "Edit Project"
        assert dialog.name_edit.text() == "Test Project"
        assert dialog.description_edit.toPlainText() == "Test Description"

    def test_validation_same_as_add_dialog(self, app):
        """Test that validation works the same as AddProjectDialog."""
        project_data = {"id": 1, "name": "Original", "description": "Original"}
        dialog = EditProjectDialog(project_data)
        
        # Test empty name validation
        dialog.name_edit.setText("")
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()

    def test_valid_edit(self, app):
        """Test valid edit acceptance."""
        project_data = {"id": 1, "name": "Original", "description": "Original"}
        dialog = EditProjectDialog(project_data)
        
        dialog.name_edit.setText("Updated Project")
        dialog.description_edit.setPlainText("Updated description")
        
        with patch.object(dialog, 'accept') as mock_accept:
            dialog._on_accept()
            mock_accept.assert_called_once()
            assert dialog.project_name == "Updated Project"
            assert dialog.project_description == "Updated description"

class TestProjectsTable:
    """Test ProjectsTable functionality."""
    
    def test_init(self, app):
        """Test table initialization."""
        table = ProjectsTable()
        assert table.columnCount() == 3
        assert table.horizontalHeaderItem(0).text() == "ID"
        assert table.horizontalHeaderItem(1).text() == "Name"
        assert table.horizontalHeaderItem(2).text() == "Description"

    def test_load_projects(self, app, sample_projects):
        """Test loading projects into table."""
        table = ProjectsTable()
        table.load_projects(sample_projects)
        
        assert table.rowCount() == 3
        assert table.item(0, 0).text() == "1"
        assert table.item(0, 1).text() == "Project Alpha"
        assert table.item(0, 2).text() == "First project"
        assert table.item(2, 2).text() == ""  # None description

    def test_selection_handling(self, app, sample_projects):
        """Test project selection handling."""
        table = ProjectsTable()
        table.load_projects(sample_projects)
        
        # Mock signal emission
        with patch.object(table, 'project_selected') as mock_signal:
            table.setCurrentCell(0, 0)
            mock_signal.emit.assert_called_once_with(1)

    def test_get_selected_project_id(self, app, sample_projects):
        """Test getting selected project ID."""
        table = ProjectsTable()
        table.load_projects(sample_projects)
        
        # No selection
        assert table.get_selected_project_id() is None
        
        # Select first row
        table.setCurrentCell(0, 0)
        assert table.get_selected_project_id() == 1
        
        # Select second row
        table.setCurrentCell(1, 0)
        assert table.get_selected_project_id() == 2

    def test_get_selected_project_data(self, app, sample_projects):
        """Test getting selected project data."""
        table = ProjectsTable()
        table.load_projects(sample_projects)
        
        # No selection
        assert table.get_selected_project_data() is None
        
        # Select first row
        table.setCurrentCell(0, 0)
        data = table.get_selected_project_data()
        assert data["id"] == 1
        assert data["name"] == "Project Alpha"
        assert data["description"] == "First project"

class TestProjectsTab:
    """Test ProjectsTab functionality."""
    
    def test_init(self, app, mock_project_manager):
        """Test tab initialization."""
        tab = ProjectsTab(mock_project_manager)
        assert tab.project_manager == mock_project_manager
        assert tab.add_button is not None
        assert tab.edit_button is not None
        assert tab.delete_button is not None
        assert tab.refresh_button is not None
        assert tab.projects_table is not None

    def test_load_projects_success(self, app, mock_project_manager, sample_projects):
        """Test successful project loading."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        
        mock_project_manager.list_projects.assert_called_once()
        assert tab.projects_table.rowCount() == 3
        assert "Loaded 3 projects" in tab.status_label.text()

    def test_load_projects_error(self, app, mock_project_manager):
        """Test project loading error handling."""
        mock_project_manager.list_projects.side_effect = Exception("Database error")
        
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
            tab = ProjectsTab(mock_project_manager)
            
            mock_critical.assert_called_once()
            assert "Error loading projects" in tab.status_label.text()

    def test_add_project_success(self, app, mock_project_manager):
        """Test successful project addition."""
        mock_project_manager.list_projects.return_value = []
        mock_project_manager.create_project.return_value = 1
        
        tab = ProjectsTab(mock_project_manager)
        
        # Mock dialog to return valid data
        with patch('src.ocr_receipt.gui.projects_tab.AddProjectDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = 1  # Accepted
            mock_dialog.get_project_name.return_value = "New Project"
            mock_dialog.get_project_description.return_value = "New Description"
            mock_dialog_class.return_value = mock_dialog
            
            tab._on_add_project()
            
            mock_project_manager.create_project.assert_called_once_with("New Project", "New Description")
            mock_project_manager.list_projects.assert_called()  # Called twice: init + refresh

    def test_add_project_validation_error(self, app, mock_project_manager):
        """Test project addition with validation error."""
        mock_project_manager.list_projects.return_value = []
        mock_project_manager.create_project.side_effect = ValueError("Project name too short")
        
        tab = ProjectsTab(mock_project_manager)
        
        with patch('src.ocr_receipt.gui.projects_tab.AddProjectDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = 1  # Accepted
            mock_dialog.get_project_name.return_value = "A"  # Too short
            mock_dialog.get_project_description.return_value = "Description"
            mock_dialog_class.return_value = mock_dialog
            
            with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
                tab._on_add_project()
                mock_warning.assert_called_once()

    def test_edit_project_success(self, app, mock_project_manager, sample_projects):
        """Test successful project editing."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        
        # Select first project
        tab.projects_table.setCurrentCell(0, 0)
        
        # Mock dialog to return valid data
        with patch('src.ocr_receipt.gui.projects_tab.EditProjectDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = 1  # Accepted
            mock_dialog.get_project_name.return_value = "Updated Project"
            mock_dialog.get_project_description.return_value = "Updated Description"
            mock_dialog_class.return_value = mock_dialog
            
            tab._on_edit_project()
            
            mock_project_manager.update_project.assert_called_once_with(1, "Updated Project", "Updated Description")

    def test_delete_project_success(self, app, mock_project_manager, sample_projects):
        """Test successful project deletion."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        
        # Select first project
        tab.projects_table.setCurrentCell(0, 0)
        
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = 16384  # Yes button
            tab._on_delete_project()
            
            mock_project_manager.delete_project.assert_called_once_with(1)

    def test_delete_project_cancelled(self, app, mock_project_manager, sample_projects):
        """Test cancelled project deletion."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        
        # Select first project
        tab.projects_table.setCurrentCell(0, 0)
        
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = 65536  # No button
            tab._on_delete_project()
            
            mock_project_manager.delete_project.assert_not_called()

    def test_project_selection(self, app, mock_project_manager, sample_projects):
        """Test project selection enables/disables buttons."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        
        # Initially disabled
        assert not tab.edit_button.isEnabled()
        assert not tab.delete_button.isEnabled()
        
        # Select a project
        tab.projects_table.setCurrentCell(0, 0)
        
        # Should be enabled
        assert tab.edit_button.isEnabled()
        assert tab.delete_button.isEnabled()

    def test_refresh_button(self, app, mock_project_manager, sample_projects):
        """Test refresh button functionality."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        
        # Clear the list and call refresh
        tab.projects_table.load_projects([])
        assert tab.projects_table.rowCount() == 0
        
        tab.refresh_button.click()
        
        # Should reload projects
        assert tab.projects_table.rowCount() == 3 
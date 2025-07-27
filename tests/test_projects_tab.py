"""
Tests for ProjectsTab and related components.
"""
import pytest
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QDialog, QMessageBox
from PyQt6.QtCore import Qt
from unittest.mock import Mock, patch, MagicMock
from ocr_receipt.gui.projects_tab import ProjectsTab
from ocr_receipt.gui.widgets.projects_table import ProjectsTable
from ocr_receipt.gui.dialogs.add_project_dialog import AddProjectDialog, EditProjectDialog
from ocr_receipt.business.project_manager import ProjectManager
from ocr_receipt.business.database_manager import DatabaseManager

@pytest.fixture
def app(qtbot):
    """Create QApplication instance for testing."""
    return QApplication.instance() or QApplication([])

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
    
    def test_init(self, qtbot, app):
        """Test dialog initialization."""
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Add Project"
        assert dialog.isModal()
        assert dialog.project_name is None
        assert dialog.project_description is None

    def test_ui_setup(self, qtbot, app):
        """Test UI components are properly set up."""
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        
        # Check that form fields exist
        assert dialog.name_edit is not None
        assert dialog.description_edit is not None
        
        # Check placeholders
        assert "Enter project name" in dialog.name_edit.placeholderText()
        assert "Enter project description" in dialog.description_edit.placeholderText()

    def test_validation_empty_name(self, qtbot, app):
        """Test validation with empty name."""
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("")
        
        # Mock QMessageBox to capture warning
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()

    def test_validation_short_name(self, qtbot, app):
        """Test validation with short name."""
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("A")
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()

    def test_validation_long_name(self, qtbot, app):
        """Test validation with long name."""
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        
        # Temporarily remove max length to test validation
        dialog.name_edit.setMaxLength(16777215)  # Qt's default max length
        dialog.name_edit.setText("A" * 101)  # 101 characters
        
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()

    def test_valid_input(self, qtbot, app):
        """Test valid input acceptance."""
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("Valid Project")
        dialog.description_edit.setPlainText("Valid description")
        
        with patch.object(dialog, 'accept') as mock_accept:
            dialog._on_accept()
            mock_accept.assert_called_once()
            assert dialog.project_name == "Valid Project"
            assert dialog.project_description == "Valid description"

    def test_empty_description(self, qtbot, app):
        """Test handling of empty description."""
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        dialog.name_edit.setText("Valid Project")
        dialog.description_edit.setPlainText("")
        
        with patch.object(dialog, 'accept') as mock_accept:
            dialog._on_accept()
            mock_accept.assert_called_once()
            assert dialog.project_name == "Valid Project"
            assert dialog.project_description is None

    def test_button_state_changes(self, qtbot, app):
        """Test OK button state changes with text input."""
        from PyQt6.QtWidgets import QDialogButtonBox
        
        dialog = AddProjectDialog()
        qtbot.addWidget(dialog)
        ok_button = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        
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
    
    def test_init_with_project_data(self, qtbot, app):
        """Test dialog initialization with project data."""
        project_data = {"id": 1, "name": "Test Project", "description": "Test Description"}
        dialog = EditProjectDialog(project_data)
        qtbot.addWidget(dialog)
        
        assert dialog.windowTitle() == "Edit Project"
        assert dialog.name_edit.text() == "Test Project"
        assert dialog.description_edit.toPlainText() == "Test Description"

    def test_validation_same_as_add_dialog(self, qtbot, app):
        """Test that validation works the same as AddProjectDialog."""
        project_data = {"id": 1, "name": "Original", "description": "Original"}
        dialog = EditProjectDialog(project_data)
        qtbot.addWidget(dialog)
        
        # Test empty name validation
        dialog.name_edit.setText("")
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._on_accept()
            mock_warning.assert_called_once()

    def test_valid_edit(self, qtbot, app):
        """Test valid edit acceptance."""
        project_data = {"id": 1, "name": "Original", "description": "Original"}
        dialog = EditProjectDialog(project_data)
        qtbot.addWidget(dialog)
        
        dialog.name_edit.setText("Updated Project")
        dialog.description_edit.setPlainText("Updated description")
        
        with patch.object(dialog, 'accept') as mock_accept:
            dialog._on_accept()
            mock_accept.assert_called_once()
            assert dialog.project_name == "Updated Project"
            assert dialog.project_description == "Updated description"

class TestProjectsTable:
    """Test ProjectsTable functionality."""
    
    def test_init(self, qtbot, app):
        """Test table initialization."""
        table = ProjectsTable()
        qtbot.addWidget(table)
        assert table.columnCount() == 2
        assert table.horizontalHeaderItem(0).text() == "Name"
        assert table.horizontalHeaderItem(1).text() == "Description"

    def test_load_projects(self, qtbot, app, sample_projects):
        """Test loading projects into table."""
        table = ProjectsTable()
        qtbot.addWidget(table)
        table.load_projects(sample_projects)
        
        assert table.rowCount() == 3
        assert table.item(0, 0).text() == "Project Alpha"
        assert table.item(0, 1).text() == "First project"
        assert table.item(2, 1).text() == ""  # None description

    def test_selection_handling(self, qtbot, app, sample_projects):
        """Test project selection handling."""
        table = ProjectsTable()
        qtbot.addWidget(table)
        table.load_projects(sample_projects)
        
        # Mock signal emission
        with patch.object(table, 'project_selected') as mock_signal:
            table.setCurrentCell(0, 0)
            mock_signal.emit.assert_called_once_with(1)

    def test_get_selected_project_id(self, qtbot, app, sample_projects):
        """Test getting selected project ID."""
        table = ProjectsTable()
        qtbot.addWidget(table)
        table.load_projects(sample_projects)
        
        # No selection
        assert table.get_selected_project_id() is None
        
        # Select first row
        table.setCurrentCell(0, 0)
        assert table.get_selected_project_id() == 1
        
        # Select second row
        table.setCurrentCell(1, 0)
        assert table.get_selected_project_id() == 2

    def test_get_selected_project_data(self, qtbot, app, sample_projects):
        """Test getting selected project data."""
        table = ProjectsTable()
        qtbot.addWidget(table)
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
    
    def test_init(self, qtbot, app, mock_project_manager):
        """Test tab initialization."""
        # Configure the mock to return an empty list to prevent Mock object len() errors
        mock_project_manager.list_projects.return_value = []
        
        tab = ProjectsTab(mock_project_manager)
        qtbot.addWidget(tab)
        assert tab.project_manager == mock_project_manager
        assert tab.add_button is not None
        assert tab.edit_button is not None
        assert tab.delete_button is not None
        assert tab.refresh_button is not None
        assert tab.projects_table is not None

    def test_load_projects_success(self, qtbot, app, mock_project_manager, sample_projects):
        """Test successful project loading."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        qtbot.addWidget(tab)
        
        mock_project_manager.list_projects.assert_called_once()
        assert tab.projects_table.rowCount() == 3
        assert "Loaded 3 projects" in tab.status_label.text()

    def test_load_projects_error(self, qtbot, app, mock_project_manager):
        """Test project loading error handling."""
        mock_project_manager.list_projects.side_effect = Exception("Database error")
        
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_critical:
            tab = ProjectsTab(mock_project_manager)
            qtbot.addWidget(tab)
            
            mock_critical.assert_called_once()
            assert "Error loading projects" in tab.status_label.text()

    def test_add_project_success(self, qtbot, app, mock_project_manager):
        """Test successful project addition."""
        mock_project_manager.list_projects.return_value = []
        mock_project_manager.create_project.return_value = 1
        
        tab = ProjectsTab(mock_project_manager)
        qtbot.addWidget(tab)
        
        # Mock dialog to return valid data
        with patch('ocr_receipt.gui.projects_tab.AddProjectDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_project_name.return_value = "New Project"
            mock_dialog.get_project_description.return_value = "New Description"
            mock_dialog_class.return_value = mock_dialog
            
            # Mock _load_projects to prevent it from being called
            with patch.object(tab, '_load_projects'):
                tab._on_add_project()
                
                mock_project_manager.create_project.assert_called_once_with("New Project", "New Description")

    def test_add_project_validation_error(self, qtbot, app, mock_project_manager):
        """Test project addition with validation error."""
        mock_project_manager.list_projects.return_value = []
        mock_project_manager.create_project.side_effect = ValueError("Project name too short")
        
        tab = ProjectsTab(mock_project_manager)
        qtbot.addWidget(tab)
        
        with patch('ocr_receipt.gui.projects_tab.AddProjectDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_project_name.return_value = "A"  # Too short
            mock_dialog.get_project_description.return_value = "Description"
            mock_dialog_class.return_value = mock_dialog
            
            with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
                # Mock _load_projects to prevent it from being called
                with patch.object(tab, '_load_projects'):
                    tab._on_add_project()
                    mock_warning.assert_called_once()

    def test_edit_project_success(self, qtbot, app, mock_project_manager, sample_projects):
        """Test successful project editing."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        qtbot.addWidget(tab)
        
        # Select first project
        tab.projects_table.setCurrentCell(0, 0)
        
        # Mock dialog to return valid data
        with patch('ocr_receipt.gui.projects_tab.EditProjectDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
            mock_dialog.get_project_name.return_value = "Updated Project"
            mock_dialog.get_project_description.return_value = "Updated Description"
            mock_dialog_class.return_value = mock_dialog
            
            # Mock _load_projects to prevent it from being called
            with patch.object(tab, '_load_projects'):
                tab._on_edit_project()
                
                mock_project_manager.update_project.assert_called_once_with(1, "Updated Project", "Updated Description")

    def test_delete_project_success(self, qtbot, app, mock_project_manager, sample_projects):
        """Test successful project deletion."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        qtbot.addWidget(tab)
        
        # Select first project
        tab.projects_table.setCurrentCell(0, 0)
        
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.Yes
            # Mock _load_projects to prevent it from being called
            with patch.object(tab, '_load_projects'):
                tab._on_delete_project()
                
                mock_project_manager.delete_project.assert_called_once_with(1)

    def test_delete_project_cancelled(self, qtbot, app, mock_project_manager, sample_projects):
        """Test cancelled project deletion."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        qtbot.addWidget(tab)
        
        # Select first project
        tab.projects_table.setCurrentCell(0, 0)
        
        with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.No
            tab._on_delete_project()
            
            mock_project_manager.delete_project.assert_not_called()

    def test_project_selection(self, qtbot, app, mock_project_manager, sample_projects):
        """Test project selection enables/disables buttons."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        qtbot.addWidget(tab)
        
        # Initially disabled
        assert not tab.edit_button.isEnabled()
        assert not tab.delete_button.isEnabled()
        
        # Select a project
        tab.projects_table.setCurrentCell(0, 0)
        
        # Should be enabled
        assert tab.edit_button.isEnabled()
        assert tab.delete_button.isEnabled()

    def test_refresh_button(self, qtbot, app, mock_project_manager, sample_projects):
        """Test refresh button functionality."""
        mock_project_manager.list_projects.return_value = sample_projects
        
        tab = ProjectsTab(mock_project_manager)
        qtbot.addWidget(tab)
        
        # Clear the list and call refresh
        tab.projects_table.load_projects([])
        assert tab.projects_table.rowCount() == 0
        
        tab.refresh_button.click()
        
        # Should reload projects
        assert tab.projects_table.rowCount() == 3 
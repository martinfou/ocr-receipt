"""
ProjectsTab: Project management interface for the OCR Invoice Parser.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QTextEdit, QDialog, QFormLayout, QDialogButtonBox,
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from typing import Optional, Dict, Any, List
from ..business.project_manager import ProjectManager
from ..utils.translation_helper import tr
import logging

logger = logging.getLogger(__name__)

class AddProjectDialog(QDialog):
    """Dialog for adding a new project."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("add_project_dialog.title"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.project_name: Optional[str] = None
        self.project_description: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("add_project_dialog.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(tr("add_project_dialog.description"))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Project name input
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr("add_project_dialog.name_placeholder"))
        self.name_edit.setMaxLength(100)
        form_layout.addRow(tr("add_project_dialog.name_label"), self.name_edit)
        
        # Project description input
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(tr("add_project_dialog.description_placeholder"))
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow(tr("add_project_dialog.description_label"), self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals
        self.name_edit.textChanged.connect(self._on_text_changed)
        
        # Set initial state
        self._on_text_changed()

    def _on_text_changed(self) -> None:
        """Handle text changes for validation."""
        text = self.name_edit.text().strip()
        ok_button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(bool(text))

    def _on_accept(self) -> None:
        """Handle accept button click with validation."""
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, tr("add_project_dialog.validation_error"), 
                              tr("add_project_dialog.enter_name"))
            self.name_edit.setFocus()
            return
        
        if len(name) < 2:
            QMessageBox.warning(self, tr("add_project_dialog.validation_error"), 
                              tr("add_project_dialog.min_length"))
            self.name_edit.setFocus()
            return
        
        if len(name) > 100:
            QMessageBox.warning(self, tr("add_project_dialog.validation_error"), 
                              tr("add_project_dialog.max_length"))
            self.name_edit.setFocus()
            return
        
        self.project_name = name
        self.project_description = description if description else None
        self.accept()

    def get_project_name(self) -> Optional[str]:
        """Get the entered project name."""
        return self.project_name

    def get_project_description(self) -> Optional[str]:
        """Get the entered project description."""
        return self.project_description

class EditProjectDialog(QDialog):
    """Dialog for editing an existing project."""
    
    def __init__(self, project_data: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.project_data = project_data
        self.setWindowTitle(tr("edit_project_dialog.title"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.project_name: Optional[str] = None
        self.project_description: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("edit_project_dialog.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Project name input
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.project_data.get('name', ''))
        self.name_edit.setPlaceholderText(tr("edit_project_dialog.name_placeholder"))
        self.name_edit.setMaxLength(100)
        form_layout.addRow(tr("edit_project_dialog.name_label"), self.name_edit)
        
        # Project description input
        self.description_edit = QTextEdit()
        self.description_edit.setText(self.project_data.get('description', ''))
        self.description_edit.setPlaceholderText(tr("edit_project_dialog.description_placeholder"))
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow(tr("edit_project_dialog.description_label"), self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals
        self.name_edit.textChanged.connect(self._on_text_changed)
        
        # Set initial state
        self._on_text_changed()

    def _on_text_changed(self) -> None:
        """Handle text changes for validation."""
        text = self.name_edit.text().strip()
        ok_button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(bool(text))

    def _on_accept(self) -> None:
        """Handle accept button click with validation."""
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, tr("edit_project_dialog.validation_error"), 
                              tr("edit_project_dialog.enter_name"))
            self.name_edit.setFocus()
            return
        
        if len(name) < 2:
            QMessageBox.warning(self, tr("edit_project_dialog.validation_error"), 
                              tr("edit_project_dialog.min_length"))
            self.name_edit.setFocus()
            return
        
        if len(name) > 100:
            QMessageBox.warning(self, tr("edit_project_dialog.validation_error"), 
                              tr("edit_project_dialog.max_length"))
            self.name_edit.setFocus()
            return
        
        self.project_name = name
        self.project_description = description if description else None
        self.accept()

    def get_project_name(self) -> Optional[str]:
        """Get the entered project name."""
        return self.project_name

    def get_project_description(self) -> Optional[str]:
        """Get the entered project description."""
        return self.project_description

class ProjectsTable(QTableWidget):
    """Table widget for displaying and managing projects."""
    
    project_selected = pyqtSignal(int)  # Emits project ID when a project is selected
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self.projects_data: List[Dict[str, Any]] = []

    def _setup_ui(self) -> None:
        """Setup the table UI."""
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels([
            tr("projects_table.id_header"),
            tr("projects_table.name_header"),
            tr("projects_table.description_header")
        ])
        
        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Set selection behavior
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def load_projects(self, projects: List[Dict[str, Any]]) -> None:
        """Load projects into the table."""
        self.projects_data = projects
        self.setRowCount(len(projects))
        
        for row, project in enumerate(projects):
            # ID column
            id_item = QTableWidgetItem(str(project['id']))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, id_item)
            
            # Name column
            name_item = QTableWidgetItem(project['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, name_item)
            
            # Description column
            description = project.get('description', '') or ''
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 2, desc_item)

    def get_selected_project_id(self) -> Optional[int]:
        """Get the ID of the currently selected project."""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.projects_data):
            return self.projects_data[current_row]['id']
        return None

    def get_selected_project_data(self) -> Optional[Dict[str, Any]]:
        """Get the data of the currently selected project."""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.projects_data):
            return self.projects_data[current_row]
        return None

    def _on_selection_changed(self) -> None:
        """Handle selection changes."""
        project_id = self.get_selected_project_id()
        if project_id is not None:
            self.project_selected.emit(project_id)

class ProjectsTab(QWidget):
    """Main projects management tab."""
    
    def __init__(self, project_manager: ProjectManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.project_manager = project_manager
        self._setup_ui()
        self._load_projects()

    def _setup_ui(self) -> None:
        """Setup the main UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header section
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(tr("projects_tab.title"))
        title_label.setObjectName("title_label")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(tr("projects_tab.subtitle"))
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setStyleSheet("color: #666;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton(tr("projects_tab.add_button"))
        self.add_button.clicked.connect(self._on_add_project)
        
        self.edit_button = QPushButton(tr("projects_tab.edit_button"))
        self.edit_button.clicked.connect(self._on_edit_project)
        self.edit_button.setEnabled(False)
        
        self.delete_button = QPushButton(tr("projects_tab.delete_button"))
        self.delete_button.clicked.connect(self._on_delete_project)
        self.delete_button.setEnabled(False)
        
        self.refresh_button = QPushButton(tr("projects_tab.refresh_button"))
        self.refresh_button.clicked.connect(self._load_projects)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
        
        # Projects table
        self.projects_table = ProjectsTable()
        self.projects_table.project_selected.connect(self._on_project_selected)
        layout.addWidget(self.projects_table)
        
        # Status bar
        self.status_label = QLabel(tr("projects_tab.status_ready"))
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def _load_projects(self) -> None:
        """Load projects from the database."""
        try:
            projects = self.project_manager.list_projects()
            self.projects_table.load_projects(projects)
            self.status_label.setText(tr("projects_tab.status_loaded").format(count=len(projects)))
        except Exception as e:
            logger.error(f"Failed to load projects: {e}")
            QMessageBox.critical(self, tr("projects_tab.error"), 
                               tr("projects_tab.load_error").format(error=str(e)))
            self.status_label.setText(tr("projects_tab.status_error"))

    def _on_add_project(self) -> None:
        """Handle add project button click."""
        dialog = AddProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                project_id = self.project_manager.create_project(
                    dialog.get_project_name(),
                    dialog.get_project_description()
                )
                self._load_projects()
                self.status_label.setText(tr("projects_tab.status_added"))
            except ValueError as e:
                QMessageBox.warning(self, tr("projects_tab.validation_error"), str(e))
            except Exception as e:
                logger.error(f"Failed to add project: {e}")
                QMessageBox.critical(self, tr("projects_tab.error"), 
                                   tr("projects_tab.add_error").format(error=str(e)))

    def _on_edit_project(self) -> None:
        """Handle edit project button click."""
        project_data = self.projects_table.get_selected_project_data()
        if not project_data:
            return
        
        dialog = EditProjectDialog(project_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.project_manager.update_project(
                    project_data['id'],
                    dialog.get_project_name(),
                    dialog.get_project_description()
                )
                self._load_projects()
                self.status_label.setText(tr("projects_tab.status_updated"))
            except ValueError as e:
                QMessageBox.warning(self, tr("projects_tab.validation_error"), str(e))
            except Exception as e:
                logger.error(f"Failed to update project: {e}")
                QMessageBox.critical(self, tr("projects_tab.error"), 
                                   tr("projects_tab.update_error").format(error=str(e)))

    def _on_delete_project(self) -> None:
        """Handle delete project button click."""
        project_data = self.projects_table.get_selected_project_data()
        if not project_data:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            tr("projects_tab.delete_confirm_title"),
            tr("projects_tab.delete_confirm_message").format(project_name=project_data['name']),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.project_manager.delete_project(project_data['id'])
                self._load_projects()
                self.status_label.setText(tr("projects_tab.status_deleted"))
            except Exception as e:
                logger.error(f"Failed to delete project: {e}")
                QMessageBox.critical(self, tr("projects_tab.error"), 
                                   tr("projects_tab.delete_error").format(error=str(e)))

    def _on_project_selected(self, project_id: int) -> None:
        """Handle project selection."""
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def update_language(self) -> None:
        """Update all text elements when language changes."""
        # Update button texts
        self.add_button.setText(tr("projects_tab.add_button"))
        self.edit_button.setText(tr("projects_tab.edit_button"))
        self.delete_button.setText(tr("projects_tab.delete_button"))
        self.refresh_button.setText(tr("projects_tab.refresh_button"))
        
        # Update title and subtitle
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(tr("projects_tab.title"))
        
        subtitle_label = self.findChild(QLabel, "subtitle_label")
        if subtitle_label:
            subtitle_label.setText(tr("projects_tab.subtitle"))
        
        # Update table headers
        self.projects_table.setHorizontalHeaderLabels([
            tr("projects_table.id_header"),
            tr("projects_table.name_header"),
            tr("projects_table.description_header")
        ])
        
        # Update status label
        if hasattr(self, 'status_label'):
            current_text = self.status_label.text()
            if "Loaded" in current_text:
                count = len(self.projects_table.projects_data)
                self.status_label.setText(tr("projects_tab.status_loaded").format(count=count))
            elif "Ready" in current_text:
                self.status_label.setText(tr("projects_tab.status_ready")) 
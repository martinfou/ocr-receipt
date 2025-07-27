"""
ProjectsTab: Project management interface for the OCR Invoice Parser.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QMessageBox, QFrame, QDialog
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any
from ..business.project_manager import ProjectManager
from ..utils.translation_helper import tr
from .widgets.projects_table import ProjectsTable
from .dialogs.add_project_dialog import AddProjectDialog, EditProjectDialog
import logging

logger = logging.getLogger(__name__)

class ProjectsTab(QWidget):
    """Main projects management tab."""
    
    projects_changed = pyqtSignal()  # Signal emitted when projects are added, edited, or deleted
    
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
        self.projects_table.project_double_clicked.connect(self._on_project_double_clicked)
        layout.addWidget(self.projects_table)
        
        # Status bar
        self.status_label = QLabel(tr("projects_tab.status_ready"))
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def _load_projects(self) -> None:
        """Load projects from the database."""
        try:
            projects = self.project_manager.list_projects()
            
            # Defensive check for mock objects or invalid data
            if not isinstance(projects, list):
                error_msg = f"Expected list from list_projects(), got {type(projects)}"
                logger.error(error_msg)
                QMessageBox.critical(self, tr("projects_tab.error"), 
                                   f"Data error: {error_msg}")
                self.status_label.setText(tr("projects_tab.status_error"))
                return
            
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
                self.projects_changed.emit()  # Notify other components
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
        
        self._edit_project_data(project_data)

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
                self.projects_changed.emit()  # Notify other components
            except Exception as e:
                logger.error(f"Failed to delete project: {e}")
                QMessageBox.critical(self, tr("projects_tab.error"), 
                                   tr("projects_tab.delete_error").format(error=str(e)))

    def _on_project_selected(self, project_id: int) -> None:
        """Handle project selection."""
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def _on_project_double_clicked(self, project_id: int) -> None:
        """Handle project double-click - open edit dialog."""
        # Find the project data for the given ID
        project_data = None
        for project in self.projects_table.projects_data:
            if project['id'] == project_id:
                project_data = project
                break
        
        if project_data:
            self._edit_project_data(project_data)
        else:
            logger.warning(f"Project with ID {project_id} not found for editing")

    def _edit_project_data(self, project_data: Dict[str, Any]) -> None:
        """Edit a specific project with the given data."""
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
                self.projects_changed.emit()  # Notify other components
            except ValueError as e:
                QMessageBox.warning(self, tr("projects_tab.validation_error"), str(e))
            except Exception as e:
                logger.error(f"Failed to update project: {e}")
                QMessageBox.critical(self, tr("projects_tab.error"), 
                                   tr("projects_tab.update_error").format(error=str(e)))

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
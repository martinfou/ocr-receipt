"""
ProjectsTable: Table widget for displaying and managing projects.
"""
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, Dict, Any, List
from ...utils.translation_helper import tr

class ProjectsTable(QTableWidget):
    """Table widget for displaying and managing projects."""
    
    project_selected = pyqtSignal(int)  # Emits project ID when a project is selected
    project_double_clicked = pyqtSignal(int)  # Emits project ID when a project is double-clicked
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self.projects_data: List[Dict[str, Any]] = []

    def _setup_ui(self) -> None:
        """Setup the table UI."""
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels([
            tr("projects_table.name_header"),
            tr("projects_table.description_header")
        ])
        
        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
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
            # Name column
            name_item = QTableWidgetItem(project['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, name_item)
            
            # Description column
            description = project.get('description', '') or ''
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, desc_item)

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

    def mouseDoubleClickEvent(self, event) -> None:
        """Handle double-click events on table rows."""
        super().mouseDoubleClickEvent(event)
        
        # Get the item that was double-clicked
        item = self.itemAt(event.pos())
        if item is not None:
            row = item.row()
            if row >= 0 and row < len(self.projects_data):
                project_id = self.projects_data[row]['id']
                self.project_double_clicked.emit(project_id) 
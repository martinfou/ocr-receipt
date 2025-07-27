"""
AddProjectDialog: Dialog for adding and editing projects.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTextEdit, QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import Optional, Dict, Any
from ...utils.translation_helper import tr

class AddProjectDialog(QDialog):
    """Dialog for adding a new project."""
    
    def __init__(self, parent=None) -> None:
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
    
    def __init__(self, project_data: Dict[str, Any], parent=None) -> None:
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
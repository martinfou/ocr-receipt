"""
AddCategoryDialog: Dialog for adding and editing categories.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTextEdit, QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import Optional, Dict, Any
from ...utils.translation_helper import tr

class AddCategoryDialog(QDialog):
    """Dialog for adding a new category."""
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("add_category_dialog.title"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.category_name: Optional[str] = None
        self.category_description: Optional[str] = None
        self.category_code: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("add_category_dialog.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(tr("add_category_dialog.description"))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Category name input
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr("add_category_dialog.name_placeholder"))
        self.name_edit.setMaxLength(100)
        form_layout.addRow(tr("add_category_dialog.name_label"), self.name_edit)
        
        # Category code input
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText(tr("add_category_dialog.code_placeholder"))
        self.code_edit.setMaxLength(20)
        form_layout.addRow(tr("add_category_dialog.code_label"), self.code_edit)
        
        # Category description input
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(tr("add_category_dialog.description_placeholder"))
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow(tr("add_category_dialog.description_label"), self.description_edit)
        
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
        code = self.code_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.enter_name"))
            self.name_edit.setFocus()
            return
        
        if len(name) < 2:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.min_length"))
            self.name_edit.setFocus()
            return
        
        if len(name) > 100:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.max_length"))
            self.name_edit.setFocus()
            return
        
        self.category_name = name
        self.category_code = code if code else None
        self.category_description = description if description else None
        self.accept()

    def get_category_name(self) -> Optional[str]:
        """Get the entered category name."""
        return self.category_name

    def get_category_code(self) -> Optional[str]:
        """Get the entered category code."""
        return self.category_code

    def get_category_description(self) -> Optional[str]:
        """Get the entered category description."""
        return self.category_description

class EditCategoryDialog(QDialog):
    """Dialog for editing an existing category."""
    
    def __init__(self, category_data: Dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self.category_data = category_data
        self.setWindowTitle(tr("edit_category_dialog.title"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.category_name: Optional[str] = None
        self.category_description: Optional[str] = None
        self.category_code: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("edit_category_dialog.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Category name input
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.category_data.get('name', ''))
        self.name_edit.setPlaceholderText(tr("edit_category_dialog.name_placeholder"))
        self.name_edit.setMaxLength(100)
        form_layout.addRow(tr("edit_category_dialog.name_label"), self.name_edit)
        
        # Category code input
        self.code_edit = QLineEdit()
        self.code_edit.setText(self.category_data.get('category_code', ''))
        self.code_edit.setPlaceholderText(tr("edit_category_dialog.code_placeholder"))
        self.code_edit.setMaxLength(20)
        form_layout.addRow(tr("edit_category_dialog.code_label"), self.code_edit)
        
        # Category description input
        self.description_edit = QTextEdit()
        self.description_edit.setText(self.category_data.get('description', ''))
        self.description_edit.setPlaceholderText(tr("edit_category_dialog.description_placeholder"))
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow(tr("edit_category_dialog.description_label"), self.description_edit)
        
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
        code = self.code_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.enter_name"))
            self.name_edit.setFocus()
            return
        
        if len(name) < 2:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.min_length"))
            self.name_edit.setFocus()
            return
        
        if len(name) > 100:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.max_length"))
            self.name_edit.setFocus()
            return
        
        self.category_name = name
        self.category_code = code if code else None
        self.category_description = description if description else None
        self.accept()

    def get_category_name(self) -> Optional[str]:
        """Get the entered category name."""
        return self.category_name

    def get_category_code(self) -> Optional[str]:
        """Get the entered category code."""
        return self.category_code

    def get_category_description(self) -> Optional[str]:
        """Get the entered category description."""
        return self.category_description 
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from typing import Optional
from ...utils.translation_helper import tr

class AddBusinessDialog(QDialog):
    """
    Dialog for adding a new business name.
    """
    def __init__(self, parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("add_business_dialog.title"))
        self.setModal(True)
        self.setMinimumWidth(350)
        self.business_name: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("add_business_dialog.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(tr("add_business_dialog.description"))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Business name input
        layout.addWidget(QLabel(tr("add_business_dialog.business_name_label")))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr("add_business_dialog.placeholder"))
        self.name_edit.setMaxLength(100)  # Reasonable limit
        layout.addWidget(self.name_edit)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(tr("add_business_dialog.add_button"))
        self.ok_button.setDefault(True)
        self.cancel_button = QPushButton(tr("add_business_dialog.cancel_button"))
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)

        # Connect signals
        self.ok_button.clicked.connect(self._on_accept)
        self.cancel_button.clicked.connect(self.reject)
        self.name_edit.textChanged.connect(self._on_text_changed)
        
        # Set initial state
        self._on_text_changed()

    def _on_text_changed(self) -> None:
        """Handle text changes for validation."""
        text = self.name_edit.text().strip()
        self.ok_button.setEnabled(bool(text))

    def _on_accept(self) -> None:
        """Handle accept button click with validation."""
        name = self.name_edit.text().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, tr("add_business_dialog.validation_error"), 
                              tr("add_business_dialog.enter_name"))
            self.name_edit.setFocus()
            return
        
        # Check for minimum length
        if len(name) < 2:
            QMessageBox.warning(self, tr("add_business_dialog.validation_error"), 
                              tr("add_business_dialog.min_length"))
            self.name_edit.setFocus()
            return
        
        # Check for maximum length
        if len(name) > 100:
            QMessageBox.warning(self, tr("add_business_dialog.validation_error"), 
                              tr("add_business_dialog.max_length"))
            self.name_edit.setFocus()
            return
        
        # Check for invalid characters (basic validation)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in name for char in invalid_chars):
            QMessageBox.warning(self, tr("add_business_dialog.validation_error"), 
                              tr("add_business_dialog.invalid_chars", chars=', '.join(invalid_chars)))
            self.name_edit.setFocus()
            return
        
        # Store the business name
        self.business_name = name
        self.accept()

    def get_business_name(self) -> Optional[str]:
        """Get the entered business name."""
        return self.business_name 
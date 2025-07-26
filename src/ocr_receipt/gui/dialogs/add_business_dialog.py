from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from typing import Optional

class AddBusinessDialog(QDialog):
    """
    Dialog for adding a new business name.
    """
    def __init__(self, parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Business")
        self.setModal(True)
        self.setMinimumWidth(350)
        self.business_name: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Add New Business")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Enter the name of the business you want to add. This will create a new business entry with an exact keyword match.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Business name input
        layout.addWidget(QLabel("Business Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter business name...")
        self.name_edit.setMaxLength(100)  # Reasonable limit
        layout.addWidget(self.name_edit)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Add Business")
        self.ok_button.setDefault(True)
        self.cancel_button = QPushButton("Cancel")
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
            QMessageBox.warning(self, "Validation Error", "Please enter a business name.")
            self.name_edit.setFocus()
            return
        
        # Check for minimum length
        if len(name) < 2:
            QMessageBox.warning(self, "Validation Error", "Business name must be at least 2 characters long.")
            self.name_edit.setFocus()
            return
        
        # Check for maximum length
        if len(name) > 100:
            QMessageBox.warning(self, "Validation Error", "Business name cannot exceed 100 characters.")
            self.name_edit.setFocus()
            return
        
        # Check for invalid characters (basic validation)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in name for char in invalid_chars):
            QMessageBox.warning(self, "Validation Error", 
                              f"Business name contains invalid characters: {', '.join(invalid_chars)}")
            self.name_edit.setFocus()
            return
        
        # Store the business name
        self.business_name = name
        self.accept()

    def get_business_name(self) -> Optional[str]:
        """Get the entered business name."""
        return self.business_name 
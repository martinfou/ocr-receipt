from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import Optional, Dict, Any

class EditKeywordDialog(QDialog):
    """
    Dialog for editing an existing keyword.
    """
    def __init__(self, keyword_data: Dict[str, Any], parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.keyword_data = keyword_data
        self.original_keyword = keyword_data.get('keyword', '')
        self.original_case_sensitive = keyword_data.get('is_case_sensitive', 0)
        self.business_name = keyword_data.get('business_name', '')
        
        self.setWindowTitle(f"Edit Keyword - {self.business_name}")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Result data
        self.edited_keyword: Optional[str] = None
        self.edited_case_sensitive: Optional[int] = None
        
        self._setup_ui()
        self._load_current_data()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Form layout for fields
        form_layout = QFormLayout()
        
        # Business name (read-only)
        self.business_label = QLabel(self.business_name)
        self.business_label.setStyleSheet("font-weight: bold; color: #666;")
        form_layout.addRow("Business:", self.business_label)
        
        # Keyword field
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("Enter keyword text...")
        form_layout.addRow("Keyword:", self.keyword_edit)
        
        # Case sensitive checkbox
        self.case_sensitive_checkbox = QCheckBox("Case sensitive")
        self.case_sensitive_checkbox.setToolTip("If checked, this keyword will only match with exact case")
        form_layout.addRow("", self.case_sensitive_checkbox)
        
        # Usage information (read-only)
        usage_count = self.keyword_data.get('usage_count', 0)
        last_used = self.keyword_data.get('last_used')
        if last_used is None:
            last_used_display = "Never"
        else:
            last_used_display = str(last_used)
        
        self.usage_label = QLabel(f"{usage_count} times")
        self.usage_label.setStyleSheet("color: #666;")
        form_layout.addRow("Usage Count:", self.usage_label)
        
        self.last_used_label = QLabel(last_used_display)
        self.last_used_label.setStyleSheet("color: #666;")
        form_layout.addRow("Last Used:", self.last_used_label)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.setDefault(True)
        self.cancel_button = QPushButton("Cancel")
        self.reset_button = QPushButton("Reset")
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.save_button.clicked.connect(self._on_save)
        self.cancel_button.clicked.connect(self.reject)
        self.reset_button.clicked.connect(self._on_reset)
        
        # Connect validation
        self.keyword_edit.textChanged.connect(self._on_text_changed)

    def _load_current_data(self) -> None:
        """Load current keyword data into the form."""
        self.keyword_edit.setText(self.original_keyword)
        self.case_sensitive_checkbox.setChecked(self.original_case_sensitive == 1)
        self._on_text_changed()

    def _on_text_changed(self) -> None:
        """Handle text changes for validation."""
        keyword = self.keyword_edit.text().strip()
        self.save_button.setEnabled(bool(keyword))

    def _on_reset(self) -> None:
        """Reset form to original values."""
        self.keyword_edit.setText(self.original_keyword)
        self.case_sensitive_checkbox.setChecked(self.original_case_sensitive == 1)
        self._on_text_changed()

    def _on_save(self) -> None:
        """Handle save button click with validation."""
        keyword = self.keyword_edit.text().strip()
        case_sensitive = 1 if self.case_sensitive_checkbox.isChecked() else 0
        
        # Validation
        if not keyword:
            QMessageBox.warning(self, "Validation Error", "Please enter a keyword.")
            self.keyword_edit.setFocus()
            return
        
        # Check if anything has changed
        if (keyword == self.original_keyword and 
            case_sensitive == self.original_case_sensitive):
            QMessageBox.information(self, "No Changes", "No changes were made to the keyword.")
            self.reject()
            return
        
        # Store the edited values
        self.edited_keyword = keyword
        self.edited_case_sensitive = case_sensitive
        
        # Accept the dialog
        self.accept()

    def get_edited_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the edited keyword data.
        Returns None if no changes were made or dialog was cancelled.
        """
        if self.edited_keyword is None:
            return None
            
        return {
            'keyword': self.edited_keyword,
            'is_case_sensitive': self.edited_case_sensitive,
            'business_name': self.business_name,
            'original_keyword': self.original_keyword,
            'original_case_sensitive': self.original_case_sensitive
        }

    def has_changes(self) -> bool:
        """Check if any changes were made."""
        if self.edited_keyword is None:
            return False
        return (self.edited_keyword != self.original_keyword or 
                self.edited_case_sensitive != self.original_case_sensitive) 
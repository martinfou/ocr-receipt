from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QFormLayout, QCheckBox
from PyQt6.QtCore import Qt
from typing import Optional, List
from ...utils.translation_helper import tr

class AddKeywordDialog(QDialog):
    """
    Dialog for adding a new keyword to an existing business.
    """
    def __init__(self, business_names: List[str], parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("add_keyword_dialog.title"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self.business_names = business_names
        self.selected_business: Optional[str] = None
        self.keyword: Optional[str] = None
        self.is_case_sensitive: bool = False
        self.match_type: str = "exact"
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("add_keyword_dialog.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(tr("add_keyword_dialog.description"))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Form layout for fields
        form_layout = QFormLayout()
        
        # Business selection dropdown
        self.business_combo = QComboBox()
        self.business_combo.addItem(tr("add_keyword_dialog.select_business"), "")
        for business_name in sorted(self.business_names):
            self.business_combo.addItem(business_name, business_name)
        form_layout.addRow(tr("add_keyword_dialog.business_label"), self.business_combo)
        
        # Keyword input
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText(tr("add_keyword_dialog.keyword_placeholder"))
        self.keyword_edit.setMaxLength(100)  # Reasonable limit
        form_layout.addRow(tr("add_keyword_dialog.keyword_label"), self.keyword_edit)
        
        # Case sensitive checkbox
        self.case_sensitive_checkbox = QCheckBox(tr("add_keyword_dialog.case_sensitive"))
        self.case_sensitive_checkbox.setToolTip(tr("add_keyword_dialog.case_sensitive_tooltip"))
        form_layout.addRow("", self.case_sensitive_checkbox)
        
        # Match type dropdown
        self.match_type_combo = QComboBox()
        self.match_type_combo.addItem("Exact Match", "exact")
        self.match_type_combo.addItem("Fuzzy Match", "fuzzy")
        self.match_type_combo.addItem("Partial Match", "partial")
        self.match_type_combo.setToolTip(tr("add_keyword_dialog.match_type_tooltip"))
        form_layout.addRow(tr("add_keyword_dialog.match_type_label"), self.match_type_combo)
        
        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(tr("add_keyword_dialog.add_button"))
        self.ok_button.setDefault(True)
        self.cancel_button = QPushButton(tr("add_keyword_dialog.cancel_button"))
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)

        # Connect signals
        self.ok_button.clicked.connect(self._on_accept)
        self.cancel_button.clicked.connect(self.reject)
        self.business_combo.currentTextChanged.connect(self._on_text_changed)
        self.keyword_edit.textChanged.connect(self._on_text_changed)
        
        # Set initial state
        self._on_text_changed()

    def _on_text_changed(self) -> None:
        """Handle text changes for validation."""
        business_selected = self.business_combo.currentData() != ""
        keyword_text = self.keyword_edit.text().strip()
        self.ok_button.setEnabled(business_selected and bool(keyword_text))

    def _on_accept(self) -> None:
        """Handle accept button click with validation."""
        business_name = self.business_combo.currentData()
        keyword_text = self.keyword_edit.text().strip()
        self.is_case_sensitive = self.case_sensitive_checkbox.isChecked()
        self.match_type = self.match_type_combo.currentData()
        
        # Validation
        if not business_name:
            QMessageBox.warning(self, tr("add_keyword_dialog.validation_error"), 
                              tr("add_keyword_dialog.select_business_error"))
            self.business_combo.setFocus()
            return
        
        if not keyword_text:
            QMessageBox.warning(self, tr("add_keyword_dialog.validation_error"), 
                              tr("add_keyword_dialog.enter_keyword"))
            self.keyword_edit.setFocus()
            return
        
        # Check for minimum length
        if len(keyword_text) < 2:
            QMessageBox.warning(self, tr("add_keyword_dialog.validation_error"), 
                              tr("add_keyword_dialog.min_length"))
            self.keyword_edit.setFocus()
            return
        
        # Check for maximum length
        if len(keyword_text) > 100:
            QMessageBox.warning(self, tr("add_keyword_dialog.validation_error"), 
                              tr("add_keyword_dialog.max_length"))
            self.keyword_edit.setFocus()
            return
        
        # Check for invalid characters (basic validation)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in keyword_text for char in invalid_chars):
            QMessageBox.warning(self, tr("add_keyword_dialog.validation_error"), 
                              tr("add_keyword_dialog.invalid_chars", chars=', '.join(invalid_chars)))
            self.keyword_edit.setFocus()
            return
        
        # Store the values
        self.selected_business = business_name
        self.keyword = keyword_text
        self.accept()

    def get_business_name(self) -> Optional[str]:
        """Get the selected business name."""
        return self.selected_business
    
    def get_keyword(self) -> Optional[str]:
        """Get the entered keyword."""
        return self.keyword
    
    def get_is_case_sensitive(self) -> bool:
        """Get the case sensitivity setting."""
        return self.is_case_sensitive
    
    def get_match_type(self) -> str:
        """Get the selected match type."""
        return self.match_type 
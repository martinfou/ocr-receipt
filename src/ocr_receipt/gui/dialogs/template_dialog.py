"""
TemplateDialog: Dialog for adding and editing file naming templates.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTextEdit, QFormLayout, QDialogButtonBox, QMessageBox,
    QComboBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
from typing import Optional, Dict, Any
from ...utils.translation_helper import tr

class TemplateDialog(QDialog):
    """Dialog for adding or editing file naming templates."""
    
    def __init__(self, template_data: Optional[Dict[str, Any]] = None, parent=None) -> None:
        super().__init__(parent)
        self.template_data = template_data or {}
        self.is_edit_mode = bool(template_data)
        
        if self.is_edit_mode:
            self.setWindowTitle(tr("template_dialog.edit_title"))
        else:
            self.setWindowTitle(tr("template_dialog.add_title"))
            
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self.template_id: Optional[str] = None
        self.template_name: Optional[str] = None
        self.template_description: Optional[str] = None
        self.template_content: Optional[str] = None
        
        self._setup_ui()
        self._load_template_data()

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("template_dialog.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Template ID (for edit mode, readonly)
        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText(tr("template_dialog.id_placeholder"))
        if self.is_edit_mode:
            self.id_edit.setReadOnly(True)
        form_layout.addRow(tr("template_dialog.id_label"), self.id_edit)
        
        # Template name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr("template_dialog.name_placeholder"))
        self.name_edit.setMaxLength(100)
        form_layout.addRow(tr("template_dialog.name_label"), self.name_edit)
        
        # Template description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(tr("template_dialog.description_placeholder"))
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow(tr("template_dialog.description_label"), self.description_edit)
        
        # Separator selection
        self.separator_combo = QComboBox()
        self.separator_combo.addItems(["_", "-", ".", " "])
        self.separator_combo.setCurrentText("_")
        form_layout.addRow(tr("template_dialog.separator_label"), self.separator_combo)
        
        # Template content
        self.template_edit = QLineEdit()
        self.template_edit.setPlaceholderText(tr("template_dialog.template_placeholder"))
        form_layout.addRow(tr("template_dialog.template_label"), self.template_edit)
        
        layout.addLayout(form_layout)
        
        # Template Variables Section
        variables_group = QGroupBox(tr("template_dialog.variables_title"))
        variables_layout = QVBoxLayout(variables_group)
        
        # Variables description
        variables_desc = QLabel(tr("template_dialog.variables_description"))
        variables_desc.setWordWrap(True)
        variables_desc.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 10px;")
        variables_layout.addWidget(variables_desc)
        
        # Variables grid
        variables_grid = QGridLayout()
        
        # Available variables
        self.variable_buttons = {}
        variables = [
            ("project", tr("template_dialog.variable_project")),
            ("documentType", tr("template_dialog.variable_document_type")),
            ("date", tr("template_dialog.variable_date")),
            ("company", tr("template_dialog.variable_company")),
            ("total", tr("template_dialog.variable_total")),
            ("invoiceNumber", tr("template_dialog.variable_invoice_number")),
            ("category", tr("template_dialog.variable_category")),
            ("categoryCode", tr("template_dialog.variable_category_code"))
        ]
        
        for i, (var_name, var_label) in enumerate(variables):
            button = QPushButton(var_label)
            button.setProperty("variable_name", var_name)
            button.clicked.connect(self._on_variable_clicked)
            button.setStyleSheet("""
                QPushButton {
                    padding: 8px 12px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: #f8f9fa;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }
                QPushButton:pressed {
                    background-color: #dee2e6;
                }
            """)
            self.variable_buttons[var_name] = button
            variables_grid.addWidget(button, i // 2, i % 2)
        
        variables_layout.addLayout(variables_grid)
        layout.addWidget(variables_group)
        
        # Help text
        help_label = QLabel(tr("template_dialog.help_text"))
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 11px; margin-top: 10px;")
        layout.addWidget(help_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals for validation
        self.name_edit.textChanged.connect(self._on_text_changed)
        self.template_edit.textChanged.connect(self._on_text_changed)
        
        # Set initial state
        self._on_text_changed()

    def _on_variable_clicked(self) -> None:
        """Handle variable button clicks."""
        button = self.sender()
        if not button:
            return
            
        variable_name = button.property("variable_name")
        if not variable_name:
            return
            
        # Get current template text
        current_template = self.template_edit.text()
        cursor_pos = self.template_edit.cursorPosition()
        
        # Get selected separator
        separator = self.separator_combo.currentText()
        
        # Create variable placeholder
        variable_placeholder = f"{{{variable_name}}}"
        
        # If template is empty, just add the variable
        if not current_template:
            new_template = variable_placeholder
        else:
            # If cursor is at the end, add separator + variable
            if cursor_pos == len(current_template):
                new_template = current_template + separator + variable_placeholder
            else:
                # Insert at cursor position
                new_template = current_template[:cursor_pos] + variable_placeholder + separator + current_template[cursor_pos:]
        
        # Update template
        self.template_edit.setText(new_template)
        
        # Set cursor position after the added variable
        new_cursor_pos = cursor_pos + len(variable_placeholder)
        if cursor_pos == len(current_template):
            new_cursor_pos += len(separator)
        self.template_edit.setCursorPosition(new_cursor_pos)
        
        # Focus back to template edit
        self.template_edit.setFocus()

    def _load_template_data(self) -> None:
        """Load existing template data for editing."""
        if not self.template_data:
            return
            
        self.id_edit.setText(self.template_data.get('id', ''))
        self.name_edit.setText(self.template_data.get('name', ''))
        self.description_edit.setPlainText(self.template_data.get('description', ''))
        self.template_edit.setText(self.template_data.get('template', ''))
        
        # Set separator based on template content
        template = self.template_data.get('template', '')
        if '_' in template:
            self.separator_combo.setCurrentText('_')
        elif '-' in template:
            self.separator_combo.setCurrentText('-')
        elif '.' in template:
            self.separator_combo.setCurrentText('.')
        elif ' ' in template:
            self.separator_combo.setCurrentText(' ')

    def _on_text_changed(self) -> None:
        """Handle text changes for validation."""
        name = self.name_edit.text().strip()
        template = self.template_edit.text().strip()
        
        ok_button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(bool(name) and bool(template))

    def _on_accept(self) -> None:
        """Handle accept button click with validation."""
        template_id = self.id_edit.text().strip()
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        template = self.template_edit.text().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, tr("template_dialog.validation_error"), 
                              tr("template_dialog.enter_name"))
            self.name_edit.setFocus()
            return
        
        if len(name) < 2:
            QMessageBox.warning(self, tr("template_dialog.validation_error"), 
                              tr("template_dialog.min_length"))
            self.name_edit.setFocus()
            return
        
        if len(name) > 100:
            QMessageBox.warning(self, tr("template_dialog.validation_error"), 
                              tr("template_dialog.max_length"))
            self.name_edit.setFocus()
            return
        
        if not template:
            QMessageBox.warning(self, tr("template_dialog.validation_error"), 
                              tr("template_dialog.enter_template"))
            self.template_edit.setFocus()
            return
        
        # Validate template format
        if not self._validate_template(template):
            QMessageBox.warning(self, tr("template_dialog.validation_error"), 
                              tr("template_dialog.invalid_template"))
            self.template_edit.setFocus()
            return
        
        # Set values
        self.template_id = template_id if template_id else name.lower().replace(' ', '_')
        self.template_name = name
        self.template_description = description if description else None
        self.template_content = template
        
        self.accept()

    def _validate_template(self, template: str) -> bool:
        """Validate the template format."""
        if not template:
            return False
        
        # Check for at least one variable
        import re
        variables = re.findall(r'\{[^}]+\}', template)
        if not variables:
            return False
        
        # Check for valid variable names
        valid_vars = {'project', 'documentType', 'date', 'company', 'total', 
                     'invoiceNumber', 'category', 'categoryCode'}
        
        for var in variables:
            var_name = var.strip('{}')
            if var_name not in valid_vars:
                return False
        
        return True

    def get_template_id(self) -> str:
        """Get the template ID."""
        return self.template_id

    def get_template_name(self) -> str:
        """Get the template name."""
        return self.template_name

    def get_template_description(self) -> Optional[str]:
        """Get the template description."""
        return self.template_description

    def get_template_content(self) -> str:
        """Get the template content."""
        return self.template_content 
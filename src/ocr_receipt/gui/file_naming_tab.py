"""
FileNamingTab: File naming template configuration and preview interface.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTextEdit, QFormLayout, QGroupBox, QCheckBox,
    QComboBox, QMessageBox, QFrame, QScrollArea, QDialog
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any, List
from ..config import ConfigManager
from ..utils.translation_helper import tr
from ..utils.filename_utils import FilenameUtils
from .dialogs.template_dialog import TemplateDialog
import logging

logger = logging.getLogger(__name__)

class FileNamingTab(QWidget):
    """File naming template configuration and preview tab."""
    
    template_changed = pyqtSignal(str)  # Signal emitted when template changes
    
    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.active_template_id: Optional[str] = None
        self._setup_ui()
        self._load_templates()
        self._update_preview()

    def _setup_ui(self) -> None:
        """Setup the main UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header section
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(tr("file_naming_tab.title"))
        title_label.setObjectName("title_label")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(tr("file_naming_tab.subtitle"))
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setStyleSheet("color: #666;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Template Management Section
        template_group = QGroupBox(tr("file_naming_tab.template_management"))
        template_layout = QVBoxLayout(template_group)
        
        # Template selection
        template_selection_layout = QHBoxLayout()
        template_selection_layout.addWidget(QLabel(tr("file_naming_tab.select_template")))
        
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self._on_template_selected)
        template_selection_layout.addWidget(self.template_combo)
        
        self.add_template_button = QPushButton(tr("file_naming_tab.add_template"))
        self.add_template_button.clicked.connect(self._on_add_template)
        template_selection_layout.addWidget(self.add_template_button)
        
        self.edit_template_button = QPushButton(tr("file_naming_tab.edit_template"))
        self.edit_template_button.clicked.connect(self._on_edit_template)
        self.edit_template_button.setEnabled(False)
        template_selection_layout.addWidget(self.edit_template_button)
        
        self.delete_template_button = QPushButton(tr("file_naming_tab.delete_template"))
        self.delete_template_button.clicked.connect(self._on_delete_template)
        self.delete_template_button.setEnabled(False)
        template_selection_layout.addWidget(self.delete_template_button)
        
        template_layout.addLayout(template_selection_layout)
        
        # Template content display
        template_content_layout = QFormLayout()
        self.template_edit = QLineEdit()
        self.template_edit.setPlaceholderText(tr("file_naming_tab.template_placeholder"))
        self.template_edit.textChanged.connect(self._on_template_changed)
        template_content_layout.addRow(tr("file_naming_tab.template_label"), self.template_edit)
        
        # Separator selection
        self.separator_combo = QComboBox()
        self.separator_combo.addItems(["_", "-", ".", " "])
        self.separator_combo.currentTextChanged.connect(self._on_template_changed)
        template_content_layout.addRow(tr("file_naming_tab.separator_label"), self.separator_combo)
        
        template_layout.addLayout(template_content_layout)
        
        layout.addWidget(template_group)
        
        # Preview Section
        preview_group = QGroupBox(tr("file_naming_tab.preview"))
        preview_layout = QVBoxLayout(preview_group)
        
        # Sample data configuration
        sample_data_label = QLabel(tr("file_naming_tab.sample_data_label"))
        sample_data_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        preview_layout.addWidget(sample_data_label)
        
        # Sample data form
        sample_form = QFormLayout()
        self.sample_project = QLineEdit("Q1_2024_Invoices")
        self.sample_project.textChanged.connect(self._update_preview)
        sample_form.addRow(tr("file_naming_tab.sample_project"), self.sample_project)
        
        self.sample_document_type = QComboBox()
        self.sample_document_type.addItems(["invoice", "credit_card", "receipt"])
        self.sample_document_type.currentTextChanged.connect(self._update_preview)
        sample_form.addRow(tr("file_naming_tab.sample_document_type"), self.sample_document_type)
        
        self.sample_date = QLineEdit("2024-01-15")
        self.sample_date.textChanged.connect(self._update_preview)
        sample_form.addRow(tr("file_naming_tab.sample_date"), self.sample_date)
        
        self.sample_company = QLineEdit("Hydro Quebec Inc")
        self.sample_company.textChanged.connect(self._update_preview)
        sample_form.addRow(tr("file_naming_tab.sample_company"), self.sample_company)
        
        self.sample_total = QLineEdit("1234.56")
        self.sample_total.textChanged.connect(self._update_preview)
        sample_form.addRow(tr("file_naming_tab.sample_total"), self.sample_total)
        
        self.sample_invoice_number = QLineEdit("INV-2024-001")
        self.sample_invoice_number.textChanged.connect(self._update_preview)
        sample_form.addRow(tr("file_naming_tab.sample_invoice_number"), self.sample_invoice_number)
        
        self.sample_category = QLineEdit("Utilities")
        self.sample_category.textChanged.connect(self._update_preview)
        sample_form.addRow(tr("file_naming_tab.sample_category"), self.sample_category)
        
        self.sample_category_code = QLineEdit("UTIL")
        self.sample_category_code.textChanged.connect(self._update_preview)
        sample_form.addRow(tr("file_naming_tab.sample_category_code"), self.sample_category_code)
        
        preview_layout.addLayout(sample_form)
        
        # Preview examples
        preview_examples_label = QLabel(tr("file_naming_tab.preview_examples"))
        preview_examples_label.setStyleSheet("font-weight: bold; margin-top: 10px; margin-bottom: 5px;")
        preview_layout.addWidget(preview_examples_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.set_active_button = QPushButton(tr("file_naming_tab.set_active"))
        self.set_active_button.clicked.connect(self._set_active_template)
        self.set_active_button.setEnabled(False)
        
        self.help_button = QPushButton(tr("file_naming_tab.help"))
        self.help_button.clicked.connect(self._show_help)
        
        button_layout.addWidget(self.set_active_button)
        button_layout.addStretch()
        button_layout.addWidget(self.help_button)
        
        layout.addLayout(button_layout)
        
        # Status bar
        self.status_label = QLabel(tr("file_naming_tab.status_ready"))
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def _load_templates(self) -> None:
        """Load templates from configuration."""
        try:
            # Load templates dictionary
            self.templates = self.config_manager.get('file_naming.templates', {})
            
            # Load active template ID
            self.active_template_id = self.config_manager.get('file_naming.active_template', 'default')
            
            # If no templates exist, create default
            if not self.templates:
                self.templates = {
                    'default': {
                        'name': 'Default Template',
                        'description': 'Standard template with project, date, company, and total',
                        'template': '{project}_{documentType}_{date}_{company}_{total}',
                        'active': True
                    }
                }
                self._save_templates()
            
            # Update UI
            self._update_template_combo()
            self._load_active_template()
            
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            self.status_label.setText(tr("file_naming_tab.status_error"))

    def _load_active_template(self) -> None:
        """Load the active template into the editor."""
        if not self.active_template_id or self.active_template_id not in self.templates:
            return
            
        template_data = self.templates[self.active_template_id]
        self.template_edit.setText(template_data.get('template', ''))
        
        # Set separator based on template
        template = template_data.get('template', '')
        if '_' in template:
            self.separator_combo.setCurrentText('_')
        elif '-' in template:
            self.separator_combo.setCurrentText('-')
        elif '.' in template:
            self.separator_combo.setCurrentText('.')
        elif ' ' in template:
            self.separator_combo.setCurrentText(' ')

    def _update_template_combo(self) -> None:
        """Update the template combo box."""
        self.template_combo.clear()
        for template_id, template_data in self.templates.items():
            self.template_combo.addItem(template_data.get('name', template_id), template_id)
        
        # Set active template
        if self.active_template_id:
            index = self.template_combo.findData(self.active_template_id)
            if index >= 0:
                self.template_combo.setCurrentIndex(index)
                # Enable buttons when template is selected
                self.edit_template_button.setEnabled(True)
                self.delete_template_button.setEnabled(True)
                self.set_active_button.setEnabled(True)

    def _save_templates(self) -> None:
        """Save templates to configuration."""
        try:
            self.config_manager.set('file_naming.templates', self.templates)
            self.config_manager.set('file_naming.active_template', self.active_template_id)
            self.config_manager.save()
        except Exception as e:
            logger.error(f"Failed to save templates: {e}")
            raise

    def _on_template_changed(self) -> None:
        """Handle template changes."""
        self._update_preview()
        self.template_changed.emit(self.template_edit.text())

    def _on_template_selected(self, template_name: str) -> None:
        """Handle template selection from combo box."""
        template_id = self.template_combo.currentData()
        if template_id and template_id in self.templates:
            self.active_template_id = template_id
            self._load_active_template()
            self._update_preview()
            
            # Enable edit and delete buttons when a template is selected
            self.edit_template_button.setEnabled(True)
            self.delete_template_button.setEnabled(True)
            self.set_active_button.setEnabled(True)
        else:
            # Disable buttons when no template is selected
            self.edit_template_button.setEnabled(False)
            self.delete_template_button.setEnabled(False)
            self.set_active_button.setEnabled(False)

    def _on_add_template(self) -> None:
        """Handle add template button click."""
        dialog = TemplateDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                template_id = dialog.get_template_id()
                template_data = {
                    'name': dialog.get_template_name(),
                    'description': dialog.get_template_description(),
                    'template': dialog.get_template_content(),
                    'active': False
                }
                
                self.templates[template_id] = template_data
                self._save_templates()
                self._update_template_combo()
                
                self.status_label.setText(tr("file_naming_tab.status_template_added"))
                
            except Exception as e:
                logger.error(f"Failed to add template: {e}")
                QMessageBox.critical(self, tr("file_naming_tab.error"),
                                   tr("file_naming_tab.add_error").format(error=str(e)))

    def _on_edit_template(self) -> None:
        """Handle edit template button click."""
        template_id = self.template_combo.currentData()
        if not template_id or template_id not in self.templates:
            return
            
        template_data = self.templates[template_id].copy()
        template_data['id'] = template_id
        
        dialog = TemplateDialog(template_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # Update template data
                self.templates[template_id] = {
                    'name': dialog.get_template_name(),
                    'description': dialog.get_template_description(),
                    'template': dialog.get_template_content(),
                    'active': template_data.get('active', False)
                }
                
                self._save_templates()
                self._update_template_combo()
                
                # If this was the active template, reload it
                if template_id == self.active_template_id:
                    self._load_active_template()
                    self._update_preview()
                
                self.status_label.setText(tr("file_naming_tab.status_template_updated"))
                
            except Exception as e:
                logger.error(f"Failed to edit template: {e}")
                QMessageBox.critical(self, tr("file_naming_tab.error"),
                                   tr("file_naming_tab.edit_error").format(error=str(e)))

    def _on_delete_template(self) -> None:
        """Handle delete template button click."""
        template_id = self.template_combo.currentData()
        if not template_id or template_id not in self.templates:
            return
            
        template_name = self.templates[template_id].get('name', template_id)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            tr("file_naming_tab.delete_confirm_title"),
            tr("file_naming_tab.delete_confirm_message").format(template_name=template_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Don't allow deletion of the last template
                if len(self.templates) <= 1:
                    QMessageBox.warning(self, tr("file_naming_tab.validation_error"),
                                      tr("file_naming_tab.cannot_delete_last"))
                    return
                
                # Remove template
                del self.templates[template_id]
                
                # If this was the active template, set another one as active
                if template_id == self.active_template_id:
                    new_active_id = next(iter(self.templates.keys()))
                    self.active_template_id = new_active_id
                    self.templates[new_active_id]['active'] = True
                
                self._save_templates()
                self._update_template_combo()
                self._load_active_template()
                self._update_preview()
                
                self.status_label.setText(tr("file_naming_tab.status_template_deleted"))
                
            except Exception as e:
                logger.error(f"Failed to delete template: {e}")
                QMessageBox.critical(self, tr("file_naming_tab.error"),
                                   tr("file_naming_tab.delete_error").format(error=str(e)))

    def _set_active_template(self) -> None:
        """Set the selected template as active."""
        template_id = self.template_combo.currentData()
        if not template_id or template_id not in self.templates:
            return
            
        try:
            # Set all templates as inactive
            for tid in self.templates:
                self.templates[tid]['active'] = False
            
            # Set selected template as active
            self.templates[template_id]['active'] = True
            self.active_template_id = template_id
            
            self._save_templates()
            self._update_template_combo()
            self._load_active_template()
            self._update_preview()
            
            self.status_label.setText(tr("file_naming_tab.status_template_activated"))
            
        except Exception as e:
            logger.error(f"Failed to set active template: {e}")
            QMessageBox.critical(self, tr("file_naming_tab.error"),
                               tr("file_naming_tab.activate_error").format(error=str(e)))

    def _update_preview(self) -> None:
        """Update the filename preview with current template and sample data."""
        try:
            template = self.template_edit.text()
            if not template:
                self.preview_text.setPlainText(tr("file_naming_tab.no_template"))
                return
            
            # Get sample data
            sample_data = {
                'project': self.sample_project.text(),
                'documentType': self.sample_document_type.currentText(),
                'date': self.sample_date.text(),
                'company': self.sample_company.text(),
                'total': self.sample_total.text(),
                'invoiceNumber': self.sample_invoice_number.text(),
                'category': self.sample_category.text(),
                'categoryCode': self.sample_category_code.text()
            }
            
            # Generate preview
            preview = FilenameUtils.generate_filename(template, sample_data)
            
            # Create multiple examples
            examples = []
            examples.append(f"Example 1: {preview}.pdf")
            
            # Generate additional examples with different data
            sample_data2 = sample_data.copy()
            sample_data2['company'] = "Royal Bank"
            sample_data2['total'] = "567.89"
            sample_data2['date'] = "2024-01-16"
            preview2 = FilenameUtils.generate_filename(template, sample_data2)
            examples.append(f"Example 2: {preview2}.pdf")
            
            sample_data3 = sample_data.copy()
            sample_data3['company'] = "Bell Canada"
            sample_data3['total'] = "234.12"
            sample_data3['date'] = "2024-01-17"
            preview3 = FilenameUtils.generate_filename(template, sample_data3)
            examples.append(f"Example 3: {preview3}.pdf")
            
            self.preview_text.setPlainText('\n'.join(examples))
            
        except Exception as e:
            logger.error(f"Failed to update preview: {e}")
            self.preview_text.setPlainText(tr("file_naming_tab.preview_error"))

    def _generate_filename(self, template: str, data: Dict[str, str]) -> str:
        """Generate filename from template and data."""
        try:
            return FilenameUtils.generate_filename(template, data)
        except Exception as e:
            logger.error(f"Failed to generate filename: {e}")
            return "error_generating_filename"

    def _clean_filename_part(self, value: str) -> str:
        """Clean a value for use in filename."""
        return FilenameUtils.clean_filename_part(value)

    def _validate_template(self, template: str) -> bool:
        """Validate the template format."""
        is_valid, _ = FilenameUtils.validate_template(template)
        return is_valid

    def _show_help(self) -> None:
        """Show help dialog for template variables."""
        help_text = tr("file_naming_tab.help_text")
        QMessageBox.information(self, tr("file_naming_tab.help_title"), help_text)

    def update_language(self) -> None:
        """Update all text elements when language changes."""
        # Update title and subtitle
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(tr("file_naming_tab.title"))
        
        subtitle_label = self.findChild(QLabel, "subtitle_label")
        if subtitle_label:
            subtitle_label.setText(tr("file_naming_tab.subtitle"))
        
        # Update button texts
        self.add_template_button.setText(tr("file_naming_tab.add_template"))
        self.edit_template_button.setText(tr("file_naming_tab.edit_template"))
        self.delete_template_button.setText(tr("file_naming_tab.delete_template"))
        self.set_active_button.setText(tr("file_naming_tab.set_active"))
        self.help_button.setText(tr("file_naming_tab.help"))
        
        # Update status label
        if hasattr(self, 'status_label'):
            self.status_label.setText(tr("file_naming_tab.status_ready")) 
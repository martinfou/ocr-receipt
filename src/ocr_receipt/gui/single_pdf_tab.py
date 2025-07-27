from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox, QSlider, QFormLayout, QFrame, QSplitter, QGridLayout, QProgressBar, QMessageBox
)
from .widgets.data_panel import DataPanel
from .widgets.pdf_preview import PDFPreview
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ocr_receipt.config import ConfigManager
from ocr_receipt.parsers.invoice_parser import InvoiceParser, InvoiceParserError
from ocr_receipt.utils.filename_utils import FilenameUtils
from pathlib import Path
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class SinglePDFTab(QWidget):
    """
    Advanced Single PDF tab with PDF preview, project settings, extracted data, file naming preview, and action buttons.
    Now uses a QSplitter with a QGridLayout for true vertical alignment of navigation and project settings.
    """
    def __init__(self, business_mapping_manager, project_manager, category_manager, config_manager=None, parent=None):
        super().__init__(parent)
        self.business_mapping_manager = business_mapping_manager
        self.project_manager = project_manager
        self.category_manager = category_manager
        self.config_manager = config_manager
        self.templates = {}
        self.active_template_id = None
        self._setup_ui()
        self._setup_connections()
        self._load_templates()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Top bar: File selection and re-process
        top_bar_widget = QWidget()
        top_bar = QHBoxLayout(top_bar_widget)
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(2)
        self.browse_button = QPushButton("📁 Browse")
        self.file_path_edit = QLineEdit()
        self.reprocess_button = QPushButton("🔄")
        self.file_path_edit.setMinimumHeight(28)
        self.browse_button.setMinimumHeight(28)
        self.reprocess_button.setMinimumHeight(28)
        self.file_path_edit.setMaximumHeight(28)
        self.browse_button.setMaximumHeight(28)
        self.reprocess_button.setMaximumHeight(28)
        top_bar.addWidget(self.browse_button)
        top_bar.addWidget(self.file_path_edit)
        top_bar.addWidget(self.reprocess_button)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Single PDF Processor"))
        top_bar_widget.setMinimumHeight(32)
        top_bar_widget.setMaximumHeight(32)
        layout.addWidget(top_bar_widget)

        # Progress indicator area
        progress_widget = QWidget()
        progress_layout = QHBoxLayout(progress_widget)
        progress_layout.setContentsMargins(8, 4, 8, 4)
        progress_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(24)
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #0078D4;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
                font-weight: bold;
                color: #333;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 2px;
            }
        """)

        self.status_label = QLabel("Ready to process PDF")
        self.status_label.setStyleSheet("color: #333; font-size: 12px; font-weight: bold; padding-left: 8px;")

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        progress_layout.addStretch()

        layout.addWidget(progress_widget)

        # Main content area: QSplitter for resizable columns
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)

        # Left and right composite widgets for grid layout
        left_grid_widget = QWidget()
        left_grid = QGridLayout(left_grid_widget)
        left_grid.setContentsMargins(0, 0, 0, 0)
        left_grid.setSpacing(8)
        right_grid_widget = QWidget()
        right_grid = QGridLayout(right_grid_widget)
        right_grid.setContentsMargins(0, 0, 0, 0)
        right_grid.setSpacing(8)

        # PDF preview and navigation controls
        self.pdf_preview = PDFPreview()
        nav_controls = self.pdf_preview.get_controls_widget()
        # Row 0: navigation/zoom controls (left), action buttons (right)
        left_grid.addWidget(nav_controls, 0, 0)
        actions = QHBoxLayout()
        self.save_button = QPushButton("💾 Save")
        self.rename_button = QPushButton("🖉 Rename File")
        self.browse_rename_button = QPushButton("📁 Browse")
        self.raw_data_button = QPushButton("📄 Raw Data")
        actions.addWidget(self.save_button)
        actions.addWidget(self.rename_button)
        actions.addWidget(self.browse_rename_button)
        actions.addWidget(self.raw_data_button)
        actions_widget = QWidget()
        actions_widget.setLayout(actions)
        right_grid.addWidget(actions_widget, 0, 0)

        # Row 1: PDF preview (left), Project Settings group (right)
        left_grid.addWidget(self.pdf_preview.pdf_label, 1, 0)
        project_group = QGroupBox("Project Settings")
        project_layout = QFormLayout(project_group)
        self.document_type_combo = QComboBox()
        self.document_type_combo.addItems(["Invoice", "Credit Card", "Other"])
        self.interactive_mode_checkbox = QCheckBox("Interactive Mode")
        self.interactive_mode_checkbox.setChecked(True)
        self.confidence_slider = QSlider()
        self.confidence_slider.setOrientation(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(50, 100)
        self.confidence_slider.setValue(80)
        self.confidence_label = QLabel("80%")
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(self.confidence_slider)
        conf_layout.addWidget(self.confidence_label)
        # Project dropdown
        from .widgets.editable_combo_box import EditableComboBox
        self.project_combo = EditableComboBox()
        project_layout.addRow("Project:", self.project_combo)
        
        project_layout.addRow("Document Type:", self.document_type_combo)
        
        # Template dropdown
        self.template_combo = QComboBox()
        self.template_combo.addItem("Default Template", "default")
        project_layout.addRow("Template:", self.template_combo)
        
        project_layout.addRow(self.interactive_mode_checkbox)
        project_layout.addRow("Confidence Threshold:", conf_layout)
        right_grid.addWidget(project_group, 1, 0)

        # Extracted data group (with confidence indicators and inline edit)
        # --- DataPanel replaces Extracted Data group ---
        extracted_info_group = QGroupBox("Extracted Information")
        extracted_info_layout = QVBoxLayout(extracted_info_group)
        self.data_panel = DataPanel()
        extracted_info_layout.addWidget(self.data_panel)
        right_grid.addWidget(extracted_info_group, 2, 0)
        # --- End DataPanel replacement ---

        # Populate project and category dropdowns from business logic
        self._populate_projects_and_categories()

        # File naming preview
        filename_group = QGroupBox("File Naming Preview")
        filename_layout = QVBoxLayout(filename_group)
        self.filename_preview = QLabel("Q1_2024_invoice_2024-01-15_hydro_quebec_$1234.56.pdf")
        filename_layout.addWidget(self.filename_preview)
        
        right_grid.addWidget(filename_group, 3, 0)

        right_grid.setRowStretch(4, 1)
        left_grid.setRowStretch(2, 1)

        splitter.addWidget(left_grid_widget)
        splitter.addWidget(right_grid_widget)
        splitter.setSizes([600, 400])  # Initial sizes
        layout.addWidget(splitter)

    def _setup_connections(self) -> None:
        self.browse_button.clicked.connect(self._on_browse_file)
        self.reprocess_button.clicked.connect(self._on_reprocess_file)
        self.browse_rename_button.clicked.connect(self._on_browse_rename)
        self.rename_button.clicked.connect(self._on_rename_file)
        self.raw_data_button.clicked.connect(self._on_raw_data)
        self.confidence_slider.valueChanged.connect(self._on_confidence_changed)
        self.template_combo.currentTextChanged.connect(self._on_template_changed)
        self.document_type_combo.currentTextChanged.connect(self._on_template_changed)
        self.project_combo.currentTextChanged.connect(self._on_template_changed)
        
        # Connect data panel fields for live filename preview updates
        if hasattr(self.data_panel, 'company_edit'):
            self.data_panel.company_edit.textChanged.connect(self._on_template_changed)
        if hasattr(self.data_panel, 'total_edit'):
            self.data_panel.total_edit.textChanged.connect(self._on_template_changed)
        if hasattr(self.data_panel, 'date_edit'):
            self.data_panel.date_edit.textChanged.connect(self._on_template_changed)
        if hasattr(self.data_panel, 'invoice_number_edit'):
            self.data_panel.invoice_number_edit.textChanged.connect(self._on_template_changed)
        if hasattr(self.data_panel, 'category_combo'):
            self.data_panel.category_combo.currentTextChanged.connect(self._on_template_changed)
        # TODO: Connect other signals for interactive features

    def _on_reprocess_file(self) -> None:
        """Handle file reprocessing with visual feedback."""
        file_path = self.file_path_edit.text()
        if file_path:
            self._process_pdf_file(file_path)
        else:
            # If no file is selected, show a test of the progress bar
            self.test_progress_bar_visibility()

    def _on_browse_file(self) -> None:
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.file_path_edit.setText(file_path)
            self._process_pdf_file(file_path)

    def _process_pdf_file(self, file_path: str) -> None:
        """Process PDF file with visual feedback."""
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtCore import QTimer
        from ocr_receipt.utils.filename_utils import PDFMetadataHandler
        
        try:
            # Stage 1: Loading
            self.show_processing_stage("loading")
            
            # Load PDF preview (this might take some time)
            self.pdf_preview.load_pdf(file_path)
            
            # Check for embedded variables in PDF metadata
            embedded_variables = PDFMetadataHandler.load_variables_from_metadata(file_path)
            if embedded_variables:
                logger.info(f"Found embedded variables in PDF: {embedded_variables}")
                self._load_embedded_variables(embedded_variables)
            
            # Stage 2: Converting to images
            self.show_processing_stage("converting")
            
            # Stage 3: OCR Processing
            self.show_processing_stage("ocr")
            
            # Stage 4: Data Extraction
            self.show_processing_stage("extracting")
            
            # Parse the PDF (this is the main processing)
            config = ConfigManager()._config  # Get full config dict
            parser = InvoiceParser(config)
            result = parser.parse(Path(file_path))
            
            # Stage 5: Business Matching
            self.show_processing_stage("matching")
            
            # Load extracted data into DataPanel
            self.data_panel.load_data({
                "company": result.get("company", ""),
                "total": result.get("total", ""),
                "date": result.get("date", ""),
                "invoice_number": result.get("invoice_number", ""),
                "company_confidence": result.get("confidence", 1.0),
                "total_confidence": result.get("confidence", 1.0),
                "date_confidence": result.get("confidence", 1.0),
                "invoice_number_confidence": result.get("confidence", 1.0)
            })
            
            # Stage 6: Complete
            self.show_processing_stage("complete")
            
        except InvoiceParserError as e:
            self.show_processing_stage("error")
            QMessageBox.critical(self, "Parsing Error", f"Failed to parse invoice: {e}")
        except Exception as e:
            self.show_processing_stage("error")
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def _load_embedded_variables(self, variables: Dict[str, str]) -> None:
        """
        Load embedded variables from PDF metadata into form fields.
        
        Args:
            variables: Dictionary of variables from PDF metadata
        """
        try:
            # Update project if available
            if 'project' in variables:
                project_name = variables['project']
                index = self.project_combo.findText(project_name)
                if index >= 0:
                    self.project_combo.setCurrentIndex(index)
                else:
                    # Add the project if it doesn't exist
                    self.project_combo.addItem(project_name)
                    self.project_combo.setCurrentText(project_name)
            
            # Update document type if available
            if 'documentType' in variables:
                doc_type = variables['documentType']
                index = self.document_type_combo.findText(doc_type)
                if index >= 0:
                    self.document_type_combo.setCurrentIndex(index)
            
            # Update category if available
            if 'category' in variables:
                category_name = variables['category']
                index = self.data_panel.category_combo.findText(category_name)
                if index >= 0:
                    self.data_panel.category_combo.setCurrentIndex(index)
            
            # Update category code if available
            if 'categoryCode' in variables:
                category_code = variables['categoryCode']
                # Assuming there's a category code field in the data panel
                if hasattr(self.data_panel, 'category_code_edit'):
                    self.data_panel.category_code_edit.setText(category_code)
            
            # Update filename preview with embedded data
            self._update_filename_preview()
            
            logger.info(f"Successfully loaded embedded variables: {variables}")
            
        except Exception as e:
            logger.error(f"Failed to load embedded variables: {e}")

    def _on_browse_rename(self) -> None:
        """Handle browse for selecting a new PDF file."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        # Open file dialog to select a PDF file
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select PDF File", 
            "", 
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            # Update the file path in the UI
            self.file_path_edit.setText(file_path)
            # Process the new PDF file
            self._process_pdf_file(file_path)

    def _on_rename_file(self) -> None:
        """Handle the rename file action."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from PyQt6.QtCore import QTimer
        
        current_file_path = self.file_path_edit.text()
        if not current_file_path:
            QMessageBox.warning(self, "No PDF File Selected", "Please select a PDF file to rename.")
            return
        
        new_file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Rename PDF File",
            current_file_path,
            "PDF Files (*.pdf)"
        )
        
        if new_file_name:
            try:
                # Ensure the new path is a PDF file
                if not new_file_name.lower().endswith('.pdf'):
                    new_file_name += '.pdf'
                
                # Check if the new path is different from the current one
                if Path(new_file_name).resolve() == Path(current_file_path).resolve():
                    QMessageBox.information(self, "No Change", "The new file name is the same as the current file name.")
                    return
                
                # Rename the file
                Path(current_file_path).rename(new_file_name)
                
                # Update the file path in the UI
                self.file_path_edit.setText(new_file_name)
                
                # Re-process the file with the new path
                self._process_pdf_file(new_file_name)
                
                QMessageBox.information(self, "File Renamed", f"File '{current_file_path}' renamed to '{new_file_name}'.")
                
            except FileNotFoundError:
                QMessageBox.warning(self, "File Not Found", f"The file '{current_file_path}' was not found.")
            except Exception as e:
                QMessageBox.critical(self, "Error Renaming File", f"Failed to rename file: {e}")

    def _on_raw_data(self) -> None:
        """Display raw extracted text from the PDF."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
        
        # Get current file path
        file_path = self.file_path_edit.text()
        if not file_path:
            QMessageBox.warning(self, "No PDF File Selected", "Please select a PDF file first to view raw data.")
            return
        
        try:
            # Extract text from PDF using OCR engine
            from ocr_receipt.core.ocr_engine import OCREngine
            from ocr_receipt.core.text_extractor import TextExtractor
            
            # Create OCR engine and text extractor
            config = ConfigManager()._config
            ocr_engine = OCREngine(config)
            text_extractor = TextExtractor(ocr_engine)
            
            # Extract text from PDF
            extracted_text = text_extractor.extract_text_from_pdf(file_path)
            
            if not extracted_text:
                QMessageBox.information(self, "No Text Found", "No text could be extracted from the PDF.")
                return
            
            # Create dialog to display raw text
            dialog = QDialog(self)
            dialog.setWindowTitle("Raw Extracted Text")
            dialog.setMinimumSize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # Add header
            header_label = QLabel(f"Raw extracted text from: {Path(file_path).name}")
            header_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
            layout.addWidget(header_label)
            
            # Add text display
            text_edit = QTextEdit()
            text_edit.setPlainText(extracted_text)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)
            
            # Add close button
            button_layout = QHBoxLayout()
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            button_layout.addStretch()
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)
            
            # Show dialog
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error displaying raw data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to extract text from PDF: {e}")

    def _on_confidence_changed(self, value: int) -> None:
        self.confidence_label.setText(f"{value}%")
        # TODO: Update confidence threshold logic

    def _on_template_changed(self) -> None:
        """Handle template selection changes."""
        # Update active template ID
        template_id = self.template_combo.currentData()
        if template_id:
            self.active_template_id = template_id
        
        # Update filename preview
        self._update_filename_preview() 

    def _populate_projects_and_categories(self):
        # Get project and category names from managers
        try:
            projects = self.project_manager.list_projects()
            
            # Defensive check for mock objects or invalid data
            if not isinstance(projects, list):
                logger.error(f"Expected list from list_projects(), got {type(projects)}")
            else:
                project_names = [p['name'] for p in projects]
                self.project_combo.set_items(project_names)
        except Exception as e:
            logger.error(f"Failed to populate projects: {e}")

        try:
            categories = self.category_manager.list_categories()
            
            # Defensive check for mock objects or invalid data
            if not isinstance(categories, list):
                logger.error(f"Expected list from list_categories(), got {type(categories)}")
            else:
                category_names = [c['name'] for c in categories]
                self.data_panel.category_combo.set_items(category_names)
        except Exception as e:
            logger.error(f"Failed to populate categories: {e}")

    def refresh_categories(self):
        """Refresh the category dropdown when categories change."""
        try:
            categories = self.category_manager.list_categories()
            
            # Defensive check for mock objects or invalid data
            if not isinstance(categories, list):
                logger.error(f"Expected list from list_categories(), got {type(categories)}")
                return
                
            category_names = [c['name'] for c in categories]
            self.data_panel.category_combo.set_items(category_names)
        except Exception as e:
            logger.error(f"Failed to refresh categories: {e}")

    def refresh_projects(self):
        """Refresh the project dropdown when projects change."""
        try:
            projects = self.project_manager.list_projects()
            
            # Defensive check for mock objects or invalid data
            if not isinstance(projects, list):
                logger.error(f"Expected list from list_projects(), got {type(projects)}")
                return
                
            project_names = [p['name'] for p in projects]
            self.project_combo.set_items(project_names)
        except Exception as e:
            logger.error(f"Failed to refresh projects: {e}")

    def show_processing_stage(self, stage: str):
        """Show appropriate status for each processing stage."""
        stages = {
            "loading": ("📄 Loading PDF file...", "Loading"),
            "converting": ("🖼️ Converting pages to images...", "Converting"), 
            "ocr": ("🔍 Running OCR analysis...", "OCR Processing"),
            "extracting": ("📊 Extracting invoice data...", "Data Extraction"),
            "matching": ("🏢 Matching business names...", "Business Matching"),
            "complete": ("✅ Processing complete!", "Complete"),
            "error": ("❌ Error occurred", "Error")
        }
        
        message, short_status = stages.get(stage, ("Processing...", "Processing"))
        self.status_label.setText(message)
        
        # Define which stages are processing stages (show progress, disable controls)
        processing_stages = ["loading", "converting", "ocr", "extracting", "matching"]
        
        if stage in processing_stages or stage not in stages:
            # Show progress bar for known processing stages or unknown stages
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.progress_bar.setValue(0)  # Ensure it starts at 0
            self._disable_controls_during_processing()
            
            # Force the progress bar to update immediately
            self.progress_bar.repaint()
        else:
            # Hide progress bar for completion stages
            self.progress_bar.setVisible(False)
            self._enable_controls_after_processing()

    def _disable_controls_during_processing(self):
        """Disable controls during processing."""
        self.browse_button.setEnabled(False)
        self.reprocess_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.rename_button.setEnabled(False)
        self.raw_data_button.setEnabled(False)

    def _enable_controls_after_processing(self):
        """Re-enable controls after processing."""
        self.browse_button.setEnabled(True)
        self.reprocess_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.rename_button.setEnabled(True)
        self.raw_data_button.setEnabled(True)

    def process_pdf_with_feedback(self, file_path: str):
        """Process PDF with visual feedback at each stage."""
        try:
            # Stage 1: Loading
            self.show_processing_stage("loading")
            
            # Stage 2: Converting to images
            self.show_processing_stage("converting")
            # PDF to image conversion happens in PDFPreview
            
            # Stage 3: OCR Processing
            self.show_processing_stage("ocr")
            # OCR processing happens in InvoiceParser
            
            # Stage 4: Data Extraction
            self.show_processing_stage("extracting")
            # Data extraction happens in InvoiceParser
            
            # Stage 5: Business Matching
            self.show_processing_stage("matching")
            # Business matching happens in InvoiceParser
            
            # Complete
            self.show_processing_stage("complete")
            
        except Exception as e:
            self.show_processing_stage("error")
            # Error handling is done in the calling method

    def test_progress_bar_visibility(self):
        """Test method to verify progress bar visibility - for debugging."""
        print("Testing progress bar visibility...")
        print(f"Progress bar visible: {self.progress_bar.isVisible()}")
        print(f"Progress bar geometry: {self.progress_bar.geometry()}")
        print(f"Progress bar parent: {self.progress_bar.parent()}")
        
        # Show the progress bar
        self.show_processing_stage("loading")
        print(f"After show_processing_stage - Progress bar visible: {self.progress_bar.isVisible()}")
        
        # Wait a bit and then hide
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.show_processing_stage("complete"))

    def _load_templates(self) -> None:
        """Load templates from configuration."""
        if not self.config_manager:
            return
            
        try:
            # Load templates dictionary
            self.templates = self.config_manager.get('file_naming.templates', {})
            
            # Load active template ID
            self.active_template_id = self.config_manager.get('file_naming.active_template', 'default')
            
            # Update template combo box
            self._update_template_combo()
            
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")

    def _update_template_combo(self) -> None:
        """Update the template combo box with available templates."""
        self.template_combo.clear()
        
        if not self.templates:
            self.template_combo.addItem("Default Template", "default")
            return
        
        for template_id, template_data in self.templates.items():
            template_name = template_data.get('name', template_id)
            self.template_combo.addItem(template_name, template_id)
        
        # Set active template
        if self.active_template_id:
            index = self.template_combo.findData(self.active_template_id)
            if index >= 0:
                self.template_combo.setCurrentIndex(index)

    def _update_filename_preview(self) -> None:
        """Update the filename preview based on current template and data."""
        try:
            if not self.templates or not self.active_template_id:
                self.filename_preview.setText("No template available")
                return
            
            template_data = self.templates.get(self.active_template_id)
            if not template_data:
                self.filename_preview.setText("Template not found")
                return
            
            template = template_data.get('template', '')
            if not template:
                self.filename_preview.setText("No template content")
                return
            
            # Get current data from the form
            data = {
                'project': self.project_combo.currentText() or 'Q1_2024_Invoices',
                'documentType': self.document_type_combo.currentText().lower() or 'invoice',
                'date': self.data_panel.date_edit.text() if hasattr(self.data_panel, 'date_edit') else '2024-01-15',
                'company': self.data_panel.company_edit.text() if hasattr(self.data_panel, 'company_edit') else 'Hydro Quebec Inc',
                'total': self.data_panel.total_edit.text() if hasattr(self.data_panel, 'total_edit') else '1234.56',
                'invoiceNumber': self.data_panel.invoice_number_edit.text() if hasattr(self.data_panel, 'invoice_number_edit') else 'INV-2024-001',
                'category': self.data_panel.category_combo.currentText() if hasattr(self.data_panel, 'category_combo') else 'Utilities',
                'categoryCode': 'UTIL'  # Default category code
            }
            
            # Generate filename
            filename = FilenameUtils.generate_filename(template, data)
            self.filename_preview.setText(f"{filename}.pdf")
            
        except Exception as e:
            logger.error(f"Failed to update filename preview: {e}")
            self.filename_preview.setText("Error generating preview")

    def _generate_filename(self, template: str, data: dict) -> str:
        """Generate filename from template and data."""
        try:
            return FilenameUtils.generate_filename(template, data)
        except Exception as e:
            logger.error(f"Failed to generate filename: {e}")
            return "error_generating_filename"

    def _clean_filename_part(self, value: str) -> str:
        """Clean a value for use in filename."""
        return FilenameUtils.clean_filename_part(value)

    def refresh_templates(self) -> None:
        """Refresh templates from configuration."""
        self._load_templates()
        self._update_filename_preview()

    def update_filename_preview(self) -> None:
        """Public method to update filename preview."""
        self._update_filename_preview() 
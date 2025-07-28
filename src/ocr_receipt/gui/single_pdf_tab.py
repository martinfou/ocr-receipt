from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox, QSlider, QFormLayout, QFrame, QSplitter, QGridLayout, QProgressBar, QMessageBox
)
from .widgets.data_panel import DataPanel
from .widgets.pdf_preview import PDFPreview
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
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
    def __init__(self, business_mapping_manager, project_manager, category_manager, document_type_manager=None, config_manager=None, parent=None):
        super().__init__(parent)
        self.business_mapping_manager = business_mapping_manager
        self.project_manager = project_manager
        self.category_manager = category_manager
        self.document_type_manager = document_type_manager
        self.config_manager = config_manager
        self.templates = {}
        self.active_template_id = None
        self._setup_ui()
        self._setup_connections()
        self._load_templates()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header section
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setMaximumHeight(60)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Single PDF Processor")
        title_label.setObjectName("title_label")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Process and extract data from individual PDF files")
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setStyleSheet("color: #666;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)



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
        
        # Action buttons and file path display
        file_path_layout = QVBoxLayout()
        
        # Action buttons (top)
        actions = QHBoxLayout()
        self.browse_rename_button = QPushButton("📁 Browse")
        self.raw_data_button = QPushButton("📄 Raw Data")
        self.rename_button = QPushButton("🖉 Rename File")
        self.ocr_button = QPushButton("🔍 OCR")
        actions.addWidget(self.browse_rename_button)
        actions.addWidget(self.raw_data_button)
        actions.addWidget(self.rename_button)
        actions.addWidget(self.ocr_button)
        file_path_layout.addLayout(actions)
        
        # File path display (bottom)
        file_path_group = QGroupBox("Current File")
        file_path_group_layout = QHBoxLayout(file_path_group)
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("No file selected")
        self.file_path_edit.setReadOnly(True)
        file_path_group_layout.addWidget(self.file_path_edit)
        file_path_layout.addWidget(file_path_group)
        
        actions_widget = QWidget()
        actions_widget.setLayout(file_path_layout)
        right_grid.addWidget(actions_widget, 0, 0)

        # Row 1: PDF preview (left), Project Settings group (right)
        left_grid.addWidget(self.pdf_preview.pdf_label, 1, 0)
        project_group = QGroupBox("Project Settings")
        project_layout = QFormLayout(project_group)
        self.document_type_combo = QComboBox()
        # Populate with document types from manager or fallback to defaults
        if self.document_type_manager:
            document_types = self.document_type_manager.get_document_type_names()
            self.document_type_combo.addItems(document_types)
        else:
            self.document_type_combo.addItems(["Invoice", "Credit Card", "Receipt", "Other"])
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
        self.data_panel = DataPanel(business_mapping_manager=self.business_mapping_manager)
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
        left_grid.setRowStretch(1, 1)

        # Add status bar and progress bar to the left grid (PDF viewer side)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        self.status_label.setMaximumHeight(25)  # Constrain height to make it thinner
        left_grid.addWidget(self.status_label, 3, 0)  # Row 3, Column 0
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # Hidden initially
        self.progress_bar.setMaximumHeight(20)
        left_grid.addWidget(self.progress_bar, 4, 0)  # Row 4, Column 0

        splitter.addWidget(left_grid_widget)
        splitter.addWidget(right_grid_widget)
        splitter.setSizes([600, 400])  # Initial sizes
        layout.addWidget(splitter)

    def _setup_connections(self) -> None:
        self.browse_rename_button.clicked.connect(self._on_browse_rename)
        self.rename_button.clicked.connect(self._on_rename_file)
        self.raw_data_button.clicked.connect(self._on_raw_data)
        self.ocr_button.clicked.connect(self._on_ocr)
        self.confidence_slider.valueChanged.connect(self._on_confidence_changed)
        self.template_combo.currentTextChanged.connect(self._on_template_changed)
        self.document_type_combo.currentTextChanged.connect(self._on_template_changed)
        self.project_combo.currentTextChanged.connect(self._on_template_changed)
        
        # Connect data panel fields for live filename preview updates
        if hasattr(self.data_panel, 'company_edit'):
            self.data_panel.company_edit.currentTextChanged.connect(self._on_template_changed)
        if hasattr(self.data_panel, 'total_edit'):
            self.data_panel.total_edit.textChanged.connect(self._on_template_changed)
        if hasattr(self.data_panel, 'date_edit'):
            self.data_panel.date_edit.textChanged.connect(self._on_template_changed)
        if hasattr(self.data_panel, 'invoice_number_edit'):
            self.data_panel.invoice_number_edit.textChanged.connect(self._on_template_changed)
        if hasattr(self.data_panel, 'category_combo'):
            self.data_panel.category_combo.currentTextChanged.connect(self._on_template_changed)
        # TODO: Connect other signals for interactive features



    def _process_pdf_file(self, file_path: str) -> None:
        """Process PDF file with visual feedback."""
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtCore import QTimer
        from ocr_receipt.utils.filename_utils import PDFMetadataHandler
        
        try:
            from PyQt6.QtCore import QCoreApplication
            
            # Stage 1: Loading
            self.show_processing_stage("loading")
            QCoreApplication.processEvents()  # Allow UI to update
            
            # Load PDF preview (this might take some time)
            self.pdf_preview.load_pdf(file_path)
            
            # Stage 2: Converting to images
            self.show_processing_stage("converting")
            QCoreApplication.processEvents()  # Allow UI to update
            
            # Parse the PDF (this is the main processing - includes OCR)
            config = ConfigManager()._config  # Get full config dict
            parser = InvoiceParser(config)
            
            # Stage 3: OCR Processing (during the actual parse)
            self.show_processing_stage("ocr")
            QCoreApplication.processEvents()  # Allow UI to update
            result = parser.parse(Path(file_path))
            
            # Stage 4: Data Extraction
            self.show_processing_stage("extracting")
            QCoreApplication.processEvents()  # Allow UI to update
            
            # Stage 5: Business Matching
            self.show_processing_stage("matching")
            QCoreApplication.processEvents()  # Allow UI to update
            
            # Check for embedded variables in PDF metadata (after OCR processing)
            embedded_variables = PDFMetadataHandler.load_variables_from_metadata(file_path)
            if embedded_variables:
                logger.info(f"Found embedded variables in PDF: {embedded_variables}")
                # Merge OCR results with embedded variables (embedded variables take precedence)
                merged_result = result.copy()
                for key, value in embedded_variables.items():
                    if key in ['company', 'total', 'date', 'invoice_number', 'check_number'] and value:
                        merged_result[key] = value
                        # Set high confidence for embedded variables
                        merged_result[f"{key}_confidence"] = 1.0
                
                # Load embedded variables into form fields
                self._load_embedded_variables(embedded_variables)
                
                # Load merged data into DataPanel
                self.data_panel.load_data({
                    "company": merged_result.get("company", ""),
                    "total": merged_result.get("total", ""),
                    "date": merged_result.get("date", ""),
                    "invoice_number": merged_result.get("invoice_number", ""),
                    "check_number": merged_result.get("check_number", ""),
                    "company_confidence": merged_result.get("company_confidence", result.get("confidence", 1.0)) if merged_result.get("company") else 0.0,
                    "total_confidence": merged_result.get("total_confidence", result.get("confidence", 1.0)) if merged_result.get("total") else 0.0,
                    "date_confidence": merged_result.get("date_confidence", result.get("confidence", 1.0)) if merged_result.get("date") else 0.0,
                    "invoice_number_confidence": merged_result.get("invoice_number_confidence", result.get("confidence", 1.0)) if merged_result.get("invoice_number") else 0.0,
                    "check_number_confidence": merged_result.get("check_number_confidence", result.get("confidence", 1.0)) if merged_result.get("check_number") else 0.0
                })
            else:
                # Load extracted data into DataPanel (OCR results only)
                self.data_panel.load_data({
                    "company": result.get("company", ""),
                    "total": result.get("total", ""),
                    "date": result.get("date", ""),
                    "invoice_number": result.get("invoice_number", ""),
                    "check_number": result.get("check_number", ""),
                    "company_confidence": result.get("confidence", 1.0) if result.get("company") else 0.0,
                    "total_confidence": result.get("confidence", 1.0) if result.get("total") else 0.0,
                    "date_confidence": result.get("confidence", 1.0) if result.get("date") else 0.0,
                    "invoice_number_confidence": result.get("confidence", 1.0) if result.get("invoice_number") else 0.0,
                    "check_number_confidence": result.get("confidence", 1.0) if result.get("check_number") else 0.0
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
            self.set_status(f"Selected file: {Path(file_path).name}")
            
            # Check if file already has metadata
            from ocr_receipt.utils.filename_utils import PDFMetadataHandler
            if PDFMetadataHandler.has_variables_in_metadata(file_path):
                self.set_status(f"File contains metadata - loading existing data")
                # Load existing metadata without OCR
                self._load_existing_metadata(file_path)
            else:
                self.set_status(f"File selected - ready for OCR processing")
                # Load PDF preview only (no OCR yet)
                self.pdf_preview.load_pdf(file_path)

    def _on_rename_file(self) -> None:
        """Handle the rename file action using the filename preview."""
        from PyQt6.QtWidgets import QMessageBox
        
        current_file_path = self.file_path_edit.text()
        if not current_file_path:
            QMessageBox.warning(self, "No PDF File Selected", "Please select a PDF file to rename.")
            return
        
        # Get the filename from the preview (remove .pdf extension if present)
        preview_filename = self.filename_preview.text()
        if not preview_filename or preview_filename == "No template available" or preview_filename == "Template not found" or preview_filename == "No template content" or preview_filename == "Error generating preview":
            QMessageBox.warning(self, "No Filename Preview", "Please ensure a valid filename template is configured and data is extracted.")
            return
        
        # Remove .pdf extension if present to get just the filename
        if preview_filename.endswith('.pdf'):
            new_filename = preview_filename[:-4]  # Remove .pdf
        else:
            new_filename = preview_filename
        
        try:
            # Use FilenameUtils to rename the file
            new_file_path = FilenameUtils.rename_file(current_file_path, new_filename)
            
            # Save current form data to PDF metadata
            from ocr_receipt.utils.filename_utils import PDFMetadataHandler
            
            # Get current data from the form
            total_value = self.data_panel.total_edit.text() if hasattr(self.data_panel, 'total_edit') else ''
            
            # Format total with 2 decimal places for filename
            if total_value:
                try:
                    total_float = float(total_value)
                    formatted_total = f"{total_float:.2f}"
                except (ValueError, TypeError):
                    formatted_total = total_value
            else:
                formatted_total = ''
            
            current_data = {
                'project': self.project_combo.currentText(),
                'documentType': self.document_type_combo.currentText().lower(),
                'date': self.data_panel.date_edit.text() if hasattr(self.data_panel, 'date_edit') else '',
                'company': self.data_panel.company_edit.currentText() if hasattr(self.data_panel, 'company_edit') else '',
                'total': formatted_total,
                'invoiceNumber': self.data_panel.invoice_number_edit.text() if hasattr(self.data_panel, 'invoice_number_edit') else '',
                'checkNumber': self.data_panel.check_number_edit.text() if hasattr(self.data_panel, 'check_number_edit') else '',
                'category': self.data_panel.category_combo.currentText() if hasattr(self.data_panel, 'category_combo') else '',
                'categoryCode': 'UTIL'  # Default category code
            }
            
            # Save to PDF metadata
            PDFMetadataHandler.save_variables_to_metadata(new_file_path, current_data)
            
            # Update the file path in the UI
            self.file_path_edit.setText(new_file_path)
            
            # Re-process the file with the new path
            self._process_pdf_file(new_file_path)
            
            self.set_status(f"File renamed to: {Path(new_file_path).name}")
            
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
            
            # Create OCR engine and text extractor using existing config manager
            if not self.config_manager:
                raise Exception("Configuration manager not available")
            
            config = self.config_manager._config
            ocr_engine = OCREngine(config)
            text_extractor = TextExtractor(config)
            
            # Extract text from PDF
            extracted_text = text_extractor.extract_from_pdf(file_path)
            
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
        # Define status messages for each stage
        stage_messages = {
            'loading': 'Loading PDF file...',
            'converting': 'Converting pages to images...',
            'ocr': 'Running OCR...',
            'extracting': 'Extracting invoice data...',
            'matching': 'Matching business names...',
            'complete': 'Processing complete',
            'error': 'Error occurred during processing'
        }
        
        # Update status message
        message = stage_messages.get(stage, 'Processing...')
        self.status_label.setText(message)
        
        # Configure progress bar based on stage
        processing_stages = ["loading", "converting", "ocr", "extracting", "matching"]
        
        if stage in processing_stages:
            # Show indeterminate progress for processing stages
            self.progress_bar.setVisible(True)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)  # Indeterminate progress
            self._disable_controls_during_processing()
        elif stage == 'complete':
            # Hide progress bar and show completion
            self.progress_bar.setVisible(False)
            self._enable_controls_after_processing()
        elif stage == 'error':
            # Hide progress bar and show error
            self.progress_bar.setVisible(False)
            self._enable_controls_after_processing()
        else:
            # Treat unknown stages as processing stages (disable controls)
            self.progress_bar.setVisible(True)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)  # Indeterminate progress
            self._disable_controls_during_processing()

    def _disable_controls_during_processing(self):
        """Disable controls during processing."""
        self.browse_rename_button.setEnabled(False)
        self.ocr_button.setEnabled(False)
        self.rename_button.setEnabled(False)
        self.raw_data_button.setEnabled(False)

    def _enable_controls_after_processing(self):
        """Re-enable controls after processing."""
        self.browse_rename_button.setEnabled(True)
        self.ocr_button.setEnabled(True)
        self.rename_button.setEnabled(True)
        self.raw_data_button.setEnabled(True)
    
    def set_status(self, message: str):
        """Set a custom status message."""
        self.status_label.setText(message)
    
    def _on_ocr(self) -> None:
        """Handle OCR button click."""
        current_file_path = self.file_path_edit.text()
        if not current_file_path:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No PDF File Selected", "Please select a PDF file to process with OCR.")
            return
        
        # Start OCR processing
        self._process_pdf_file(current_file_path)
    
    def _load_existing_metadata(self, file_path: str) -> None:
        """Load existing metadata from PDF without running OCR."""
        from ocr_receipt.utils.filename_utils import PDFMetadataHandler
        
        try:
            # Load PDF preview
            self.pdf_preview.load_pdf(file_path)
            
            # Load existing metadata
            embedded_variables = PDFMetadataHandler.load_variables_from_metadata(file_path)
            if embedded_variables:
                logger.info(f"Loaded existing metadata: {embedded_variables}")
                
                # Load embedded variables into form fields
                self._load_embedded_variables(embedded_variables)
                
                # Load data into DataPanel
                self.data_panel.load_data({
                    "company": embedded_variables.get("company", ""),
                    "total": embedded_variables.get("total", ""),
                    "date": embedded_variables.get("date", ""),
                    "invoice_number": embedded_variables.get("invoice_number", ""),
                    "check_number": embedded_variables.get("check_number", ""),
                    "company_confidence": 1.0 if embedded_variables.get("company") else 0.0,  # High confidence only if data exists
                    "total_confidence": 1.0 if embedded_variables.get("total") else 0.0,
                    "date_confidence": 1.0 if embedded_variables.get("date") else 0.0,
                    "invoice_number_confidence": 1.0 if embedded_variables.get("invoice_number") else 0.0,
                    "check_number_confidence": 1.0 if embedded_variables.get("check_number") else 0.0
                })
                
                self.set_status("Existing metadata loaded successfully")
            else:
                self.set_status("No metadata found in file")
                
        except Exception as e:
            logger.error(f"Failed to load existing metadata: {e}")
            self.set_status(f"Error loading metadata: {e}")





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
            total_value = self.data_panel.total_edit.text() if hasattr(self.data_panel, 'total_edit') else '1234.56'
            
            # Format total with 2 decimal places for filename
            if total_value:
                try:
                    total_float = float(total_value)
                    formatted_total = f"{total_float:.2f}"
                except (ValueError, TypeError):
                    formatted_total = total_value
            else:
                formatted_total = '1234.56'
            
            data = {
                'project': self.project_combo.currentText() or 'Q1_2024_Invoices',
                'documentType': self.document_type_combo.currentText().lower() or 'invoice',
                'date': self.data_panel.date_edit.text() if hasattr(self.data_panel, 'date_edit') else '2024-01-15',
                'company': self.data_panel.company_edit.currentText() if hasattr(self.data_panel, 'company_edit') else 'Hydro Quebec Inc',
                'total': formatted_total,
                'invoiceNumber': self.data_panel.invoice_number_edit.text() if hasattr(self.data_panel, 'invoice_number_edit') else 'INV-2024-001',
                'checkNumber': self.data_panel.check_number_edit.text() if hasattr(self.data_panel, 'check_number_edit') else 'CHK-2024-001',
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
        """Refresh templates when they change."""
        self._load_templates()
        self._update_template_combo()
        self._update_filename_preview()

    def refresh_company_dropdown(self) -> None:
        """Refresh the company dropdown when businesses are modified."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Refreshing company dropdown")
        
        if hasattr(self, 'data_panel'):
            # Store current text before refreshing
            current_text = self.data_panel.company_edit.currentText()
            logger.info(f"Current company text: {current_text}")
            
            # Get businesses before refresh
            businesses_before = []
            for i in range(self.data_panel.company_edit.count()):
                businesses_before.append(self.data_panel.company_edit.itemText(i))
            logger.info(f"Businesses before refresh: {businesses_before}")
            
            self.data_panel._populate_company_dropdown()
            
            # Get businesses after refresh
            businesses_after = []
            for i in range(self.data_panel.company_edit.count()):
                businesses_after.append(self.data_panel.company_edit.itemText(i))
            logger.info(f"Businesses after refresh: {businesses_after}")
            
            # Restore current text if it still exists in the dropdown
            if current_text:
                index = self.data_panel.company_edit.findText(current_text)
                if index >= 0:
                    self.data_panel.company_edit.setCurrentIndex(index)
                    logger.info(f"Restored current text '{current_text}' at index {index}")
                else:
                    # If the text is not in the dropdown anymore, set it as current text
                    self.data_panel.company_edit.setCurrentText(current_text)
                    logger.info(f"Set current text to '{current_text}' (not in dropdown)")
        else:
            logger.warning("Data panel not available for company dropdown refresh")

    def update_filename_preview(self) -> None:
        """Update the filename preview."""
        self._update_filename_preview()
    
    def refresh_document_types(self) -> None:
        """Refresh the document type dropdown with current document types."""
        try:
            # Get document types from the manager (assuming it's passed to this tab)
            if hasattr(self, 'document_type_manager'):
                document_types = self.document_type_manager.get_document_type_names()
            else:
                # Fallback to hardcoded values if manager not available
                document_types = ["Invoice", "Credit Card", "Receipt", "Other"]
            
            # Store current selection
            current_text = self.document_type_combo.currentText()
            
            # Clear and repopulate
            self.document_type_combo.clear()
            self.document_type_combo.addItems(document_types)
            
            # Restore selection if it still exists
            if current_text:
                index = self.document_type_combo.findText(current_text)
                if index >= 0:
                    self.document_type_combo.setCurrentIndex(index)
        except Exception as e:
            logger.error(f"Error refreshing document type dropdown: {e}") 
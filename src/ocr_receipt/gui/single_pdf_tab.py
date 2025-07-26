from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox, QSlider, QFormLayout, QFrame, QSplitter, QGridLayout, QProgressBar
)
from .widgets.data_panel import DataPanel
from .widgets.pdf_preview import PDFPreview
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ocr_receipt.config import ConfigManager
from ocr_receipt.parsers.invoice_parser import InvoiceParser, InvoiceParserError
from pathlib import Path

class SinglePDFTab(QWidget):
    """
    Advanced Single PDF tab with PDF preview, project settings, extracted data, file naming preview, and action buttons.
    Now uses a QSplitter with a QGridLayout for true vertical alignment of navigation and project settings.
    """
    def __init__(self, business_mapping_manager, project_manager, category_manager, parent=None):
        super().__init__(parent)
        self.business_mapping_manager = business_mapping_manager
        self.project_manager = project_manager
        self.category_manager = category_manager
        self._setup_ui()
        self._setup_connections()

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
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 2px;
            }
        """)

        self.status_label = QLabel("Ready to process PDF")
        self.status_label.setStyleSheet("color: #666; font-size: 11px; padding-left: 8px;")

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
        self.export_button = QPushButton("📊 Export")
        actions.addWidget(self.save_button)
        actions.addWidget(self.rename_button)
        actions.addWidget(self.export_button)
        actions_widget = QWidget()
        actions_widget.setLayout(actions)
        right_grid.addWidget(actions_widget, 0, 0)

        # Row 1: PDF preview (left), Project Settings group (right)
        left_grid.addWidget(self.pdf_preview.pdf_label, 1, 0)
        project_group = QGroupBox("Project Settings")
        project_layout = QFormLayout(project_group)
        self.project_name_edit = QLineEdit()
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
        project_layout.addRow("Project Name:", self.project_name_edit)
        project_layout.addRow("Document Type:", self.document_type_combo)
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
        self.confidence_slider.valueChanged.connect(self._on_confidence_changed)
        # TODO: Connect other signals for interactive features

    def _on_reprocess_file(self) -> None:
        """Handle file reprocessing with visual feedback."""
        file_path = self.file_path_edit.text()
        if file_path:
            self._process_pdf_file(file_path)

    def _on_browse_file(self) -> None:
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.file_path_edit.setText(file_path)
            self._process_pdf_file(file_path)

    def _process_pdf_file(self, file_path: str) -> None:
        """Process PDF file with visual feedback."""
        from PyQt6.QtWidgets import QMessageBox
        
        try:
            # Stage 1: Loading
            self.show_processing_stage("loading")
            
            # Load PDF preview
            self.pdf_preview.load_pdf(file_path)
            
            # Stage 2: Converting to images
            self.show_processing_stage("converting")
            
            # Stage 3: OCR Processing
            self.show_processing_stage("ocr")
            
            # Stage 4: Data Extraction
            self.show_processing_stage("extracting")
            
            # Parse the PDF
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

    def _on_confidence_changed(self, value: int) -> None:
        self.confidence_label.setText(f"{value}%")
        # TODO: Update confidence threshold logic 

    def _populate_projects_and_categories(self):
        # Get project and category names from managers
        projects = self.project_manager.list_projects()
        project_names = [p['name'] for p in projects]
        self.data_panel.project_combo.set_items(project_names)

        categories = self.category_manager.list_categories()
        category_names = [c['name'] for c in categories]
        self.data_panel.category_combo.set_items(category_names)

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
            self._disable_controls_during_processing()
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
        self.export_button.setEnabled(False)

    def _enable_controls_after_processing(self):
        """Re-enable controls after processing."""
        self.browse_button.setEnabled(True)
        self.reprocess_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.rename_button.setEnabled(True)
        self.export_button.setEnabled(True)

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
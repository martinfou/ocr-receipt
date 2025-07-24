from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox, QSlider, QFormLayout, QFrame, QSplitter, QGridLayout
)
from .widgets.data_panel import DataPanel
from .widgets.pdf_preview import PDFPreview
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class SinglePDFTab(QWidget):
    """
    Advanced Single PDF tab with PDF preview, project settings, extracted data, file naming preview, and action buttons.
    Now uses a QSplitter with a QGridLayout for true vertical alignment of navigation and project settings.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
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
        data_group = QGroupBox("Extracted Data")
        data_layout = QFormLayout(data_group)
        self.company_edit = QLineEdit()
        self.company_conf = QLabel("[✓]")
        company_row = QHBoxLayout()
        company_row.addWidget(self.company_edit)
        company_row.addWidget(self.company_conf)
        self.date_edit = QLineEdit()
        self.date_conf = QLabel("[✓]")
        date_row = QHBoxLayout()
        date_row.addWidget(self.date_edit)
        date_row.addWidget(self.date_conf)
        self.total_edit = QLineEdit()
        self.total_conf = QLabel("[✓]")
        total_row = QHBoxLayout()
        total_row.addWidget(self.total_edit)
        total_row.addWidget(self.total_conf)
        self.invoice_edit = QLineEdit()
        self.invoice_conf = QLabel("[⚠️]")
        invoice_row = QHBoxLayout()
        invoice_row.addWidget(self.invoice_edit)
        invoice_row.addWidget(self.invoice_conf)
        data_layout.addRow("Company:", company_row)
        data_layout.addRow("Date:", date_row)
        data_layout.addRow("Total:", total_row)
        data_layout.addRow("Invoice #:", invoice_row)
        right_grid.addWidget(data_group, 2, 0)

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
        self.confidence_slider.valueChanged.connect(self._on_confidence_changed)
        # TODO: Connect other signals for interactive features

    def _on_browse_file(self) -> None:
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.file_path_edit.setText(file_path)
            self.pdf_preview.load_pdf(file_path)
            # TODO: Trigger OCR and data extraction

    def _on_confidence_changed(self, value: int) -> None:
        self.confidence_label.setText(f"{value}%")
        # TODO: Update confidence threshold logic 
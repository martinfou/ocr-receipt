from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from .editable_combo_box import EditableComboBox

class DataPanel(QWidget):
    """
    Enhanced panel for displaying and editing extracted data with confidence indicators and inline edit/confirm.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Company field with confidence and actions
        self.company_edit = QLineEdit()
        self.company_conf = QLabel()
        self.company_confirm_btn = QPushButton("✓")
        company_row = QHBoxLayout()
        company_row.addWidget(self.company_edit)
        company_row.addWidget(self.company_conf)
        company_row.addWidget(self.company_confirm_btn)
        form_layout.addRow("Company:", company_row)

        # Total field
        self.total_edit = QLineEdit()
        self.total_conf = QLabel()
        self.total_confirm_btn = QPushButton("✓")
        total_row = QHBoxLayout()
        total_row.addWidget(self.total_edit)
        total_row.addWidget(self.total_conf)
        total_row.addWidget(self.total_confirm_btn)
        form_layout.addRow("Total:", total_row)

        # Date field
        self.date_edit = QLineEdit()
        self.date_conf = QLabel()
        self.date_confirm_btn = QPushButton("✓")
        date_row = QHBoxLayout()
        date_row.addWidget(self.date_edit)
        date_row.addWidget(self.date_conf)
        date_row.addWidget(self.date_confirm_btn)
        form_layout.addRow("Date:", date_row)

        # Invoice number field
        self.invoice_number_edit = QLineEdit()
        self.invoice_number_conf = QLabel()
        self.invoice_confirm_btn = QPushButton("✓")
        invoice_row = QHBoxLayout()
        invoice_row.addWidget(self.invoice_number_edit)
        invoice_row.addWidget(self.invoice_number_conf)
        invoice_row.addWidget(self.invoice_confirm_btn)
        form_layout.addRow("Invoice Number:", invoice_row)

        # Category dropdown (for assigning categories to invoices)
        self.category_combo = EditableComboBox()
        form_layout.addRow("Category:", self.category_combo)

        layout.addLayout(form_layout)

        self.filename_preview = QLabel()
        layout.addWidget(self.filename_preview)

    def set_field(self, field: str, value: str, confidence: float = 1.0, low_conf_threshold: float = 0.8):
        """
        Set the value and confidence for a field. Highlights if confidence is low.
        """
        edit = getattr(self, f"{field}_edit", None)
        conf_label = getattr(self, f"{field}_conf", None)
        print(f"[DEBUG] set_field: field={field}, edit={edit}, conf_label={conf_label}, value={value}")
        if edit and conf_label:
            edit.setText(str(value))
            if confidence >= low_conf_threshold:
                conf_label.setText("[✓]")
                edit.setStyleSheet("")
            else:
                conf_label.setText("[⚠️]")
                edit.setStyleSheet("background: #fff3cd;")

    def load_data(self, data: dict):
        self.set_field("company", data.get("company", ""), data.get("company_confidence", 1.0))
        self.set_field("total", str(data.get("total", "")), data.get("total_confidence", 1.0))
        self.set_field("date", data.get("date", ""), data.get("date_confidence", 1.0))
        self.set_field("invoice_number", data.get("invoice_number", ""), data.get("invoice_number_confidence", 1.0)) 
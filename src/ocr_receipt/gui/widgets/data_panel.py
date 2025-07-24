from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QLabel
from .editable_combo_box import EditableComboBox

class DataPanel(QWidget):
    """Panel for displaying and editing extracted data."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.company_edit = QLineEdit()
        form_layout.addRow("Company:", self.company_edit)

        self.total_edit = QLineEdit()
        form_layout.addRow("Total:", self.total_edit)

        self.date_edit = QLineEdit()
        form_layout.addRow("Date:", self.date_edit)

        self.invoice_number_edit = QLineEdit()
        form_layout.addRow("Invoice Number:", self.invoice_number_edit)

        self.project_combo = EditableComboBox()
        form_layout.addRow("Project:", self.project_combo)

        self.category_combo = EditableComboBox()
        form_layout.addRow("Category:", self.category_combo)

        layout.addLayout(form_layout)

        self.filename_preview = QLabel()
        layout.addWidget(self.filename_preview)

    def load_data(self, data: dict):
        self.company_edit.setText(data.get("company", ""))
        self.total_edit.setText(str(data.get("total", "")))
        self.date_edit.setText(data.get("date", ""))
        self.invoice_number_edit.setText(data.get("invoice_number", "")) 
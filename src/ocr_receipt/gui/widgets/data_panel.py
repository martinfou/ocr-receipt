from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout, QComboBox, QCompleter, QMessageBox
from PyQt6.QtCore import Qt
from .editable_combo_box import EditableComboBox

class DataPanel(QWidget):
    """
    Enhanced panel for displaying and editing extracted data with confidence indicators and inline edit/confirm.
    """
    def __init__(self, business_mapping_manager=None, parent=None):
        super().__init__(parent)
        self.business_mapping_manager = business_mapping_manager
        self._setup_ui()
        self._populate_company_dropdown()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Company field with confidence and actions
        self.company_edit = EditableComboBox()
        self.company_edit.setMinimumWidth(250)  # Increase width for more space
        self.company_edit.setMaximumWidth(300)
        self.company_edit.setEditable(True)
        self.company_edit.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.company_edit.setCompleter(None)  # We'll set this after populating
        self.company_edit.lineEdit().returnPressed.connect(self._on_company_enter_pressed)
        self.company_conf = QLabel()
        self.company_conf.setMinimumWidth(50)  # Fixed width for confidence label
        self.company_conf.setMaximumWidth(50)
        self.company_confirm_btn = QPushButton("✓")
        self.company_confirm_btn.setFixedSize(30, 30)  # Square button
        company_row = QHBoxLayout()
        company_row.addWidget(self.company_edit)
        company_row.addWidget(self.company_conf)
        company_row.addWidget(self.company_confirm_btn)
        form_layout.addRow("Company:", company_row)

        # Total field
        self.total_edit = QLineEdit()
        self.total_edit.setMinimumWidth(250)  # Increase width for more space
        self.total_edit.setMaximumWidth(300)
        self.total_conf = QLabel()
        self.total_conf.setMinimumWidth(50)  # Fixed width for confidence label
        self.total_conf.setMaximumWidth(50)
        self.total_confirm_btn = QPushButton("✓")
        self.total_confirm_btn.setFixedSize(30, 30)  # Square button
        total_row = QHBoxLayout()
        total_row.addWidget(self.total_edit)
        total_row.addWidget(self.total_conf)
        total_row.addWidget(self.total_confirm_btn)
        form_layout.addRow("Total:", total_row)

        # Date field
        self.date_edit = QLineEdit()
        self.date_edit.setMinimumWidth(250)  # Increase width for more space
        self.date_edit.setMaximumWidth(300)
        self.date_conf = QLabel()
        self.date_conf.setMinimumWidth(50)  # Fixed width for confidence label
        self.date_conf.setMaximumWidth(50)
        self.date_confirm_btn = QPushButton("✓")
        self.date_confirm_btn.setFixedSize(30, 30)  # Square button
        date_row = QHBoxLayout()
        date_row.addWidget(self.date_edit)
        date_row.addWidget(self.date_conf)
        date_row.addWidget(self.date_confirm_btn)
        form_layout.addRow("Date:", date_row)

        # Invoice number field
        self.invoice_number_edit = QLineEdit()
        self.invoice_number_edit.setMinimumWidth(250)  # Increase width for more space
        self.invoice_number_edit.setMaximumWidth(300)
        self.invoice_number_conf = QLabel()
        self.invoice_number_conf.setMinimumWidth(50)  # Fixed width for confidence label
        self.invoice_number_conf.setMaximumWidth(50)
        self.invoice_number_confirm_btn = QPushButton("✓")
        self.invoice_number_confirm_btn.setFixedSize(30, 30)  # Square button
        invoice_row = QHBoxLayout()
        invoice_row.addWidget(self.invoice_number_edit)
        invoice_row.addWidget(self.invoice_number_conf)
        invoice_row.addWidget(self.invoice_number_confirm_btn)
        form_layout.addRow("Invoice Number:", invoice_row)

        # Check number field
        self.check_number_edit = QLineEdit()
        self.check_number_edit.setMinimumWidth(250)  # Increase width for more space
        self.check_number_edit.setMaximumWidth(300)
        self.check_number_conf = QLabel()
        self.check_number_conf.setMinimumWidth(50)  # Fixed width for confidence label
        self.check_number_conf.setMaximumWidth(50)
        self.check_number_confirm_btn = QPushButton("✓")
        self.check_number_confirm_btn.setFixedSize(30, 30)  # Square button
        check_number_row = QHBoxLayout()
        check_number_row.addWidget(self.check_number_edit)
        check_number_row.addWidget(self.check_number_conf)
        check_number_row.addWidget(self.check_number_confirm_btn)
        form_layout.addRow("Check Number:", check_number_row)

        # Category dropdown (for assigning categories to invoices)
        self.category_combo = EditableComboBox()
        self.category_combo.setMinimumWidth(250)  # Increase width for more space
        self.category_combo.setMaximumWidth(300)
        form_layout.addRow("Category:", self.category_combo)

        layout.addLayout(form_layout)

        self.filename_preview = QLabel()
        layout.addWidget(self.filename_preview)

    def _populate_company_dropdown(self):
        import logging
        logger = logging.getLogger(__name__)
        
        if self.business_mapping_manager:
            logger.info("Populating company dropdown")
            self.company_edit.clear()
            business_names = self.business_mapping_manager.get_business_names()
            logger.info(f"Retrieved business names: {business_names}")
            self.company_edit.addItems(business_names)
            
            # Set completer for auto-complete functionality
            completer = QCompleter(business_names)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.company_edit.setCompleter(completer)
            logger.info(f"Company dropdown populated with {len(business_names)} businesses")
        else:
            logger.warning("Business mapping manager not available for company dropdown population")

    def _on_company_enter_pressed(self):
        """Handle Enter key press in company field and ask for confirmation to add new business."""
        current_text = self.company_edit.currentText().strip()
        if not current_text or not self.business_mapping_manager:
            return
            
        try:
            # Check if this business already exists
            existing_businesses = self.business_mapping_manager.get_business_names()
            if current_text not in existing_businesses:
                # Ask user for confirmation
                reply = QMessageBox.question(
                    self, 
                    "Add New Business", 
                    f"Do you want to add '{current_text}' as a new business?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Add the new business to the database
                    self.business_mapping_manager.add_business(current_text)
                    # Refresh the dropdown to include the new business
                    self._populate_company_dropdown()
                    # Set the current text back to the new business
                    self.company_edit.setCurrentText(current_text)
                    QMessageBox.information(self, "Success", f"Business '{current_text}' has been added successfully!")
        except Exception as e:
            # Log error and show user-friendly message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to add business '{current_text}': {e}")
            QMessageBox.critical(self, "Error", f"Failed to add business '{current_text}': {e}")

    def set_field(self, field: str, value: str, confidence: float = 1.0, low_conf_threshold: float = 0.8):
        """
        Set the value and confidence for a field. Shows confidence percentage and appropriate icon.
        """
        edit = getattr(self, f"{field}_edit", None)
        conf_label = getattr(self, f"{field}_conf", None)
        confirm_btn = getattr(self, f"{field}_confirm_btn", None)
        
        if edit and conf_label and confirm_btn:
            # Set the value based on widget type
            if hasattr(edit, 'setCurrentText'):  # EditableComboBox
                edit.setCurrentText(str(value))
            else:  # QLineEdit
                edit.setText(str(value))
            
            # Convert confidence to percentage
            confidence_percent = int(confidence * 100)
            
            # Set confidence percentage text
            if confidence == 0.0:
                conf_label.setText("—")  # Show dash for no data
            else:
                conf_label.setText(f"{confidence_percent}%")
            
            # Set icon and color based on confidence level
            if confidence == 0.0:  # No data extracted
                confirm_btn.setText("—")
                confirm_btn.setStyleSheet("background-color: #6c757d; color: white; border: none; padding: 2px 6px; border-radius: 3px;")
                edit.setStyleSheet("background: #f8f9fa; color: #6c757d;")
            elif confidence >= 0.9:  # 90% or higher
                confirm_btn.setText("✓")
                confirm_btn.setStyleSheet("background-color: #28a745; color: white; border: none; padding: 2px 6px; border-radius: 3px;")
                edit.setStyleSheet("")
            elif confidence >= 0.6:  # 60% to 89%
                confirm_btn.setText("⚠")
                confirm_btn.setStyleSheet("background-color: #ffc107; color: black; border: none; padding: 2px 6px; border-radius: 3px;")
                edit.setStyleSheet("background: #fff3cd;")
            else:  # Below 60%
                confirm_btn.setText("✗")
                confirm_btn.setStyleSheet("background-color: #dc3545; color: white; border: none; padding: 2px 6px; border-radius: 3px;")
                edit.setStyleSheet("background: #f8d7da;")

    def load_data(self, data: dict):
        self.set_field("company", data.get("company", ""), data.get("company_confidence", 1.0))
        
        # Format total with 2 decimal places
        total_value = data.get("total", "")
        if total_value:
            try:
                # Convert to float and format with 2 decimal places
                total_float = float(total_value)
                formatted_total = f"{total_float:.2f}"
            except (ValueError, TypeError):
                formatted_total = str(total_value)
        else:
            formatted_total = ""
        
        self.set_field("total", formatted_total, data.get("total_confidence", 1.0))
        self.set_field("date", data.get("date", ""), data.get("date_confidence", 1.0))
        self.set_field("invoice_number", data.get("invoice_number", ""), data.get("invoice_number_confidence", 1.0))
        self.set_field("check_number", data.get("check_number", ""), data.get("check_number_confidence", 1.0)) 
"""
Document Types Tab for OCR Invoice Parser
Provides GUI for managing document types
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel, QFormLayout,
    QLineEdit, QTextEdit, QCheckBox, QDialog, QDialogButtonBox,
    QSplitter, QGroupBox, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any
import logging

from ocr_receipt.utils.translation_helper import tr

logger = logging.getLogger(__name__)


class AddDocumentTypeDialog(QDialog):
    """Dialog for adding a new document type."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("document_types_tab.add_document_type"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr("document_types_tab.enter_name"))
        form_layout.addRow(tr("document_types_tab.name"), self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText(tr("document_types_tab.enter_description"))
        form_layout.addRow(tr("document_types_tab.description"), self.description_edit)
        
        self.is_default_checkbox = QCheckBox(tr("document_types_tab.set_as_default"))
        form_layout.addRow("", self.is_default_checkbox)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect validation
        self.name_edit.textChanged.connect(self._validate_input)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self._ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
    
    def _validate_input(self):
        """Validate input and enable/disable OK button."""
        name = self.name_edit.text().strip()
        self._ok_button.setEnabled(bool(name))
    
    def get_data(self) -> Dict[str, Any]:
        """Get the entered data."""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'is_default': self.is_default_checkbox.isChecked()
        }


class EditDocumentTypeDialog(QDialog):
    """Dialog for editing an existing document type."""
    
    def __init__(self, document_type_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.document_type_data = document_type_data
        self.setWindowTitle(tr("document_types_tab.edit_document_type"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr("document_types_tab.enter_name"))
        form_layout.addRow(tr("document_types_tab.name"), self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText(tr("document_types_tab.enter_description"))
        form_layout.addRow(tr("document_types_tab.description"), self.description_edit)
        
        self.is_default_checkbox = QCheckBox(tr("document_types_tab.set_as_default"))
        form_layout.addRow("", self.is_default_checkbox)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect validation
        self.name_edit.textChanged.connect(self._validate_input)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self._ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
    
    def _load_data(self):
        """Load existing data into the form."""
        self.name_edit.setText(self.document_type_data.get('name', ''))
        self.description_edit.setPlainText(self.document_type_data.get('description', ''))
        self.is_default_checkbox.setChecked(self.document_type_data.get('is_default', False))
        self._validate_input()
    
    def _validate_input(self):
        """Validate input and enable/disable OK button."""
        name = self.name_edit.text().strip()
        self._ok_button.setEnabled(bool(name))
    
    def get_data(self) -> Dict[str, Any]:
        """Get the entered data."""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'is_default': self.is_default_checkbox.isChecked()
        }


class DocumentTypesTab(QWidget):
    """
    Tab for managing document types.
    Provides CRUD operations for document types.
    """
    
    # Signals
    document_types_changed = pyqtSignal()  # Emitted when document types are modified
    
    def __init__(self, document_type_manager):
        super().__init__()
        self.document_type_manager = document_type_manager
        self._setup_ui()
        self._setup_connections()
        self._refresh_table()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header section
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setMaximumHeight(60)  # Constrain header height to match other tabs
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(tr("document_types_tab.title"))
        title_label.setObjectName("title_label")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(tr("document_types_tab.description"))
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setStyleSheet("color: #666;")
        subtitle_label.setWordWrap(True)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Splitter for table and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Table
        table_group = QGroupBox(tr("document_types_tab.document_types"))
        table_layout = QVBoxLayout(table_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(tr("document_types_tab.add"))
        self.edit_button = QPushButton(tr("document_types_tab.edit"))
        self.delete_button = QPushButton(tr("document_types_tab.delete"))
        self.set_default_button = QPushButton(tr("document_types_tab.set_default"))
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.set_default_button)
        button_layout.addStretch()
        
        table_layout.addLayout(button_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            tr("document_types_tab.name"),
            tr("document_types_tab.description"),
            tr("document_types_tab.default"),
            tr("document_types_tab.sort_order")
        ])
        
        # Table properties
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        table_layout.addWidget(self.table)
        splitter.addWidget(table_group)
        
        # Right side - Details
        details_group = QGroupBox(tr("document_types_tab.details"))
        details_layout = QVBoxLayout(details_group)
        
        self.details_label = QLabel(tr("document_types_tab.select_document_type"))
        self.details_label.setWordWrap(True)
        details_layout.addWidget(self.details_label)
        
        splitter.addWidget(details_group)
        
        # Set splitter proportions
        splitter.setSizes([600, 300])
        
        # Status bar
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        
        self._update_button_states()
    
    def _setup_connections(self):
        """Set up signal connections."""
        self.add_button.clicked.connect(self._on_add_document_type)
        self.edit_button.clicked.connect(self._on_edit_document_type)
        self.delete_button.clicked.connect(self._on_delete_document_type)
        self.set_default_button.clicked.connect(self._on_set_default_document_type)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Connect manager signals
        self.document_type_manager.document_types_changed.connect(self._refresh_table)
    
    def _refresh_table(self):
        """Refresh the document types table."""
        try:
            document_types = self.document_type_manager.get_all_document_types()
            
            self.table.setRowCount(len(document_types))
            
            for row, doc_type in enumerate(document_types):
                # Name
                name_item = QTableWidgetItem(doc_type['name'])
                name_item.setData(Qt.ItemDataRole.UserRole, doc_type)
                self.table.setItem(row, 0, name_item)
                
                # Description
                description_item = QTableWidgetItem(doc_type.get('description', ''))
                self.table.setItem(row, 1, description_item)
                
                # Default
                default_item = QTableWidgetItem("✓" if doc_type.get('is_default') else "")
                default_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, default_item)
                
                # Sort order
                sort_order_item = QTableWidgetItem(str(doc_type.get('sort_order', 0)))
                sort_order_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 3, sort_order_item)
            
            self._update_status()
            self._update_button_states()
            
        except Exception as e:
            logger.error(f"Error refreshing document types table: {e}")
            self.status_label.setText(tr("document_types_tab.error_loading"))
    
    def _update_status(self):
        """Update the status label."""
        count = self.table.rowCount()
        self.status_label.setText(tr("document_types_tab.status").format(count=count))
    
    def _update_button_states(self):
        """Update button enabled states based on selection."""
        has_selection = self.table.currentRow() >= 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.set_default_button.setEnabled(has_selection)
    
    def _on_selection_changed(self):
        """Handle table selection changes."""
        self._update_button_states()
        self._update_details()
    
    def _update_details(self):
        """Update the details panel."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            item = self.table.item(current_row, 0)
            if item:
                doc_type = item.data(Qt.ItemDataRole.UserRole)
                details_text = f"""
<b>{tr("document_types_tab.name")}:</b> {doc_type['name']}<br>
<b>{tr("document_types_tab.description")}:</b> {doc_type.get('description', '')}<br>
<b>{tr("document_types_tab.default")}:</b> {"✓" if doc_type.get('is_default') else "✗"}<br>
<b>{tr("document_types_tab.sort_order")}:</b> {doc_type.get('sort_order', 0)}
                """
                self.details_label.setText(details_text)
        else:
            self.details_label.setText(tr("document_types_tab.select_document_type"))
    
    def _on_add_document_type(self):
        """Handle add document type button click."""
        dialog = AddDocumentTypeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            success = self.document_type_manager.add_document_type(
                name=data['name'],
                description=data['description'],
                is_default=data['is_default']
            )
            
            if success:
                self.status_label.setText(tr("document_types_tab.added_successfully"))
                self.document_types_changed.emit()
            else:
                QMessageBox.warning(
                    self,
                    tr("document_types_tab.error"),
                    tr("document_types_tab.add_failed")
                )
    
    def _on_edit_document_type(self):
        """Handle edit document type button click."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        item = self.table.item(current_row, 0)
        if not item:
            return
        
        doc_type = item.data(Qt.ItemDataRole.UserRole)
        old_name = doc_type['name']
        
        dialog = EditDocumentTypeDialog(doc_type, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            success = self.document_type_manager.update_document_type(
                old_name=old_name,
                new_name=data['name'],
                description=data['description'],
                is_default=data['is_default']
            )
            
            if success:
                self.status_label.setText(tr("document_types_tab.updated_successfully"))
                self.document_types_changed.emit()
            else:
                QMessageBox.warning(
                    self,
                    tr("document_types_tab.error"),
                    tr("document_types_tab.update_failed")
                )
    
    def _on_delete_document_type(self):
        """Handle delete document type button click."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        item = self.table.item(current_row, 0)
        if not item:
            return
        
        doc_type = item.data(Qt.ItemDataRole.UserRole)
        name = doc_type['name']
        
        # Check if it's the default type
        if doc_type.get('is_default'):
            QMessageBox.warning(
                self,
                tr("document_types_tab.cannot_delete_default"),
                tr("document_types_tab.cannot_delete_default_message")
            )
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            tr("document_types_tab.confirm_delete"),
            tr("document_types_tab.confirm_delete_message").format(name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.document_type_manager.delete_document_type(name)
            
            if success:
                self.status_label.setText(tr("document_types_tab.deleted_successfully"))
                self.document_types_changed.emit()
            else:
                QMessageBox.warning(
                    self,
                    tr("document_types_tab.error"),
                    tr("document_types_tab.delete_failed")
                )
    
    def _on_set_default_document_type(self):
        """Handle set default document type button click."""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        item = self.table.item(current_row, 0)
        if not item:
            return
        
        doc_type = item.data(Qt.ItemDataRole.UserRole)
        name = doc_type['name']
        
        # Check if already default
        if doc_type.get('is_default'):
            QMessageBox.information(
                self,
                tr("document_types_tab.already_default"),
                tr("document_types_tab.already_default_message").format(name=name)
            )
            return
        
        success = self.document_type_manager.set_default_document_type(name)
        
        if success:
            self.status_label.setText(tr("document_types_tab.default_set_successfully"))
            self.document_types_changed.emit()
        else:
            QMessageBox.warning(
                self,
                tr("document_types_tab.error"),
                tr("document_types_tab.set_default_failed")
            ) 
"""
CategoriesTab: Category management interface for the OCR Invoice Parser.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QLineEdit, QTextEdit, QDialog, QFormLayout, QDialogButtonBox,
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from typing import Optional, Dict, Any, List
from ..business.category_manager import CategoryManager
from ..utils.translation_helper import tr
import logging

logger = logging.getLogger(__name__)

class AddCategoryDialog(QDialog):
    """Dialog for adding a new category."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("add_category_dialog.title"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.category_name: Optional[str] = None
        self.category_description: Optional[str] = None
        self.category_code: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("add_category_dialog.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(tr("add_category_dialog.description"))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Category name input
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr("add_category_dialog.name_placeholder"))
        self.name_edit.setMaxLength(100)
        form_layout.addRow(tr("add_category_dialog.name_label"), self.name_edit)
        
        # Category code input
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText(tr("add_category_dialog.code_placeholder"))
        self.code_edit.setMaxLength(20)
        form_layout.addRow(tr("add_category_dialog.code_label"), self.code_edit)
        
        # Category description input
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(tr("add_category_dialog.description_placeholder"))
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow(tr("add_category_dialog.description_label"), self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals
        self.name_edit.textChanged.connect(self._on_text_changed)
        
        # Set initial state
        self._on_text_changed()

    def _on_text_changed(self) -> None:
        """Handle text changes for validation."""
        text = self.name_edit.text().strip()
        ok_button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(bool(text))

    def _on_accept(self) -> None:
        """Handle accept button click with validation."""
        name = self.name_edit.text().strip()
        code = self.code_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.enter_name"))
            self.name_edit.setFocus()
            return
        
        if len(name) < 2:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.min_length"))
            self.name_edit.setFocus()
            return
        
        if len(name) > 100:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.max_length"))
            self.name_edit.setFocus()
            return
        
        self.category_name = name
        self.category_code = code if code else None
        self.category_description = description if description else None
        self.accept()

    def get_category_name(self) -> Optional[str]:
        """Get the entered category name."""
        return self.category_name

    def get_category_code(self) -> Optional[str]:
        """Get the entered category code."""
        return self.category_code

    def get_category_description(self) -> Optional[str]:
        """Get the entered category description."""
        return self.category_description

class EditCategoryDialog(QDialog):
    """Dialog for editing an existing category."""
    
    def __init__(self, category_data: Dict[str, Any], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.category_data = category_data
        self.setWindowTitle(tr("edit_category_dialog.title"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.category_name: Optional[str] = None
        self.category_description: Optional[str] = None
        self.category_code: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("edit_category_dialog.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Category name input
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.category_data.get('name', ''))
        self.name_edit.setPlaceholderText(tr("edit_category_dialog.name_placeholder"))
        self.name_edit.setMaxLength(100)
        form_layout.addRow(tr("edit_category_dialog.name_label"), self.name_edit)
        
        # Category code input
        self.code_edit = QLineEdit()
        self.code_edit.setText(self.category_data.get('category_code', ''))
        self.code_edit.setPlaceholderText(tr("edit_category_dialog.code_placeholder"))
        self.code_edit.setMaxLength(20)
        form_layout.addRow(tr("edit_category_dialog.code_label"), self.code_edit)
        
        # Category description input
        self.description_edit = QTextEdit()
        self.description_edit.setText(self.category_data.get('description', ''))
        self.description_edit.setPlaceholderText(tr("edit_category_dialog.description_placeholder"))
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow(tr("edit_category_dialog.description_label"), self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals
        self.name_edit.textChanged.connect(self._on_text_changed)
        
        # Set initial state
        self._on_text_changed()

    def _on_text_changed(self) -> None:
        """Handle text changes for validation."""
        text = self.name_edit.text().strip()
        ok_button = self.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(bool(text))

    def _on_accept(self) -> None:
        """Handle accept button click with validation."""
        name = self.name_edit.text().strip()
        code = self.code_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        # Validation
        if not name:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.enter_name"))
            self.name_edit.setFocus()
            return
        
        if len(name) < 2:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.min_length"))
            self.name_edit.setFocus()
            return
        
        if len(name) > 100:
            QMessageBox.warning(self, tr("add_category_dialog.validation_error"), 
                              tr("add_category_dialog.max_length"))
            self.name_edit.setFocus()
            return
        
        self.category_name = name
        self.category_code = code if code else None
        self.category_description = description if description else None
        self.accept()

    def get_category_name(self) -> Optional[str]:
        """Get the entered category name."""
        return self.category_name

    def get_category_code(self) -> Optional[str]:
        """Get the entered category code."""
        return self.category_code

    def get_category_description(self) -> Optional[str]:
        """Get the entered category description."""
        return self.category_description

class CategoriesTable(QTableWidget):
    """Table widget for displaying and managing categories."""
    
    category_selected = pyqtSignal(int)  # Emits category ID when a category is selected
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self.categories_data: List[Dict[str, Any]] = []

    def _setup_ui(self) -> None:
        """Setup the table UI."""
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels([
            tr("categories_table.id_header"),
            tr("categories_table.name_header"),
            tr("categories_table.code_header"),
            tr("categories_table.description_header")
        ])
        
        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        # Set selection behavior
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def load_categories(self, categories: List[Dict[str, Any]]) -> None:
        """Load categories into the table."""
        self.categories_data = categories
        self.setRowCount(len(categories))
        
        for row, category in enumerate(categories):
            # ID column
            id_item = QTableWidgetItem(str(category['id']))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, id_item)
            
            # Name column
            name_item = QTableWidgetItem(category['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, name_item)
            
            # Code column
            code = category.get('category_code', '') or ''
            code_item = QTableWidgetItem(code)
            code_item.setFlags(code_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 2, code_item)
            
            # Description column
            description = category.get('description', '') or ''
            desc_item = QTableWidgetItem(description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 3, desc_item)

    def get_selected_category_id(self) -> Optional[int]:
        """Get the ID of the currently selected category."""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.categories_data):
            return self.categories_data[current_row]['id']
        return None

    def get_selected_category_data(self) -> Optional[Dict[str, Any]]:
        """Get the data of the currently selected category."""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.categories_data):
            return self.categories_data[current_row]
        return None

    def _on_selection_changed(self) -> None:
        """Handle selection changes."""
        category_id = self.get_selected_category_id()
        if category_id is not None:
            self.category_selected.emit(category_id)

class CategoriesTab(QWidget):
    """Main categories management tab."""
    
    categories_changed = pyqtSignal()  # Signal emitted when categories are added, edited, or deleted
    
    def __init__(self, category_manager: CategoryManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.category_manager = category_manager
        self._setup_ui()
        self._load_categories()

    def _setup_ui(self) -> None:
        """Setup the main UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header section
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(tr("categories_tab.title"))
        title_label.setObjectName("title_label")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(tr("categories_tab.subtitle"))
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setStyleSheet("color: #666;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton(tr("categories_tab.add_button"))
        self.add_button.clicked.connect(self._on_add_category)
        
        self.edit_button = QPushButton(tr("categories_tab.edit_button"))
        self.edit_button.clicked.connect(self._on_edit_category)
        self.edit_button.setEnabled(False)
        
        self.delete_button = QPushButton(tr("categories_tab.delete_button"))
        self.delete_button.clicked.connect(self._on_delete_category)
        self.delete_button.setEnabled(False)
        
        self.refresh_button = QPushButton(tr("categories_tab.refresh_button"))
        self.refresh_button.clicked.connect(self._load_categories)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
        
        # Categories table
        self.categories_table = CategoriesTable()
        self.categories_table.category_selected.connect(self._on_category_selected)
        layout.addWidget(self.categories_table)
        
        # Status bar
        self.status_label = QLabel(tr("categories_tab.status_ready"))
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def _load_categories(self) -> None:
        """Load categories from the database."""
        try:
            categories = self.category_manager.list_categories()
            self.categories_table.load_categories(categories)
            self.status_label.setText(tr("categories_tab.status_loaded").format(count=len(categories)))
        except Exception as e:
            logger.error(f"Failed to load categories: {e}")
            QMessageBox.critical(self, tr("categories_tab.error"), 
                               tr("categories_tab.load_error").format(error=str(e)))
            self.status_label.setText(tr("categories_tab.status_error"))

    def _on_add_category(self) -> None:
        """Handle add category button click."""
        dialog = AddCategoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                category_id = self.category_manager.create_category(
                    dialog.get_category_name(),
                    dialog.get_category_description(),
                    dialog.get_category_code()
                )
                self._load_categories()
                self.status_label.setText(tr("categories_tab.status_added"))
                self.categories_changed.emit()  # Notify other components
            except ValueError as e:
                QMessageBox.warning(self, tr("categories_tab.validation_error"), str(e))
            except Exception as e:
                logger.error(f"Failed to add category: {e}")
                QMessageBox.critical(self, tr("categories_tab.error"), 
                                   tr("categories_tab.add_error").format(error=str(e)))

    def _on_edit_category(self) -> None:
        """Handle edit category button click."""
        category_data = self.categories_table.get_selected_category_data()
        if not category_data:
            return
        
        dialog = EditCategoryDialog(category_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.category_manager.update_category(
                    category_data['id'],
                    dialog.get_category_name(),
                    dialog.get_category_description(),
                    dialog.get_category_code()
                )
                self._load_categories()
                self.status_label.setText(tr("categories_tab.status_updated"))
                self.categories_changed.emit()  # Notify other components
            except ValueError as e:
                QMessageBox.warning(self, tr("categories_tab.validation_error"), str(e))
            except Exception as e:
                logger.error(f"Failed to update category: {e}")
                QMessageBox.critical(self, tr("categories_tab.error"), 
                                   tr("categories_tab.update_error").format(error=str(e)))

    def _on_delete_category(self) -> None:
        """Handle delete category button click."""
        category_data = self.categories_table.get_selected_category_data()
        if not category_data:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            tr("categories_tab.delete_confirm_title"),
            tr("categories_tab.delete_confirm_message").format(category_name=category_data['name']),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.category_manager.delete_category(category_data['id'])
                self._load_categories()
                self.status_label.setText(tr("categories_tab.status_deleted"))
                self.categories_changed.emit()  # Notify other components
            except Exception as e:
                logger.error(f"Failed to delete category: {e}")
                QMessageBox.critical(self, tr("categories_tab.error"), 
                                   tr("categories_tab.delete_error").format(error=str(e)))

    def _on_category_selected(self, category_id: int) -> None:
        """Handle category selection."""
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def update_language(self) -> None:
        """Update all text elements when language changes."""
        # Update button texts
        self.add_button.setText(tr("categories_tab.add_button"))
        self.edit_button.setText(tr("categories_tab.edit_button"))
        self.delete_button.setText(tr("categories_tab.delete_button"))
        self.refresh_button.setText(tr("categories_tab.refresh_button"))
        
        # Update title and subtitle
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(tr("categories_tab.title"))
        
        subtitle_label = self.findChild(QLabel, "subtitle_label")
        if subtitle_label:
            subtitle_label.setText(tr("categories_tab.subtitle"))
        
        # Update table headers
        self.categories_table.setHorizontalHeaderLabels([
            tr("categories_table.id_header"),
            tr("categories_table.name_header"),
            tr("categories_table.code_header"),
            tr("categories_table.description_header")
        ])
        
        # Update status label
        if hasattr(self, 'status_label'):
            current_text = self.status_label.text()
            if "Loaded" in current_text:
                count = len(self.categories_table.categories_data)
                self.status_label.setText(tr("categories_tab.status_loaded").format(count=count))
            elif "Ready" in current_text:
                self.status_label.setText(tr("categories_tab.status_ready")) 
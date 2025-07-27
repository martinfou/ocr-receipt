"""
CategoriesTab: Category management interface for the OCR Invoice Parser.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QMessageBox, QFrame, QDialog
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any
from ..business.category_manager import CategoryManager
from ..utils.translation_helper import tr
from .widgets.categories_table import CategoriesTable
from .dialogs.add_category_dialog import AddCategoryDialog, EditCategoryDialog
import logging

logger = logging.getLogger(__name__)

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
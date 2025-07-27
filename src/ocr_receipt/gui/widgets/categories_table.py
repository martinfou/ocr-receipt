"""
CategoriesTable: Table widget for displaying and managing categories.
"""
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, Dict, Any, List
from ...utils.translation_helper import tr

class CategoriesTable(QTableWidget):
    """Table widget for displaying and managing categories."""
    
    category_selected = pyqtSignal(int)  # Emits category ID when a category is selected
    
    def __init__(self, parent=None) -> None:
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
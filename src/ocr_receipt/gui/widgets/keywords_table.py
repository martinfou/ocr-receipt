from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QWidget, QHeaderView, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QFont
from typing import List, Dict, Any, Optional
from datetime import datetime

class KeywordsTable(QTableWidget):
    """
    Enhanced table widget for displaying business keywords and their properties.
    Includes sorting, filtering, and selection handling.
    """
    
    # Signals
    keyword_selected = pyqtSignal(dict)  # Emitted when a keyword is selected
    keyword_double_clicked = pyqtSignal(dict)  # Emitted when a keyword is double-clicked
    selection_changed = pyqtSignal(list)  # Emitted when selection changes
    
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._original_data = []  # Store original data for filtering
        self._filtered_data = []  # Store filtered data
        self._setup_ui()
        self._setup_connections()
        
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Set up table structure
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "Business",
            "Keyword", 
            "Match Type",
            "Case Sensitive",
            "Usage Count",
            "Last Used"
        ])
        
        # Configure table behavior
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(True)
        
        # Configure header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set minimum size
        self.setMinimumHeight(200)
        
    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        
    def _setup_filter_widgets(self, parent_widget: QWidget) -> None:
        """Set up filter widgets in the parent widget."""
        # Create filter layout
        filter_layout = QHBoxLayout()
        
        # Search filter
        filter_layout.addWidget(QLabel("Search:"))
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Search keywords or businesses...")
        self.search_filter.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_filter)
        
        # Business filter
        filter_layout.addWidget(QLabel("Business:"))
        self.business_filter = QComboBox()
        self.business_filter.addItem("All Businesses")
        self.business_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.business_filter)
        
        # Match type filter
        filter_layout.addWidget(QLabel("Match Type:"))
        self.match_type_filter = QComboBox()
        self.match_type_filter.addItems(["All Types", "exact", "fuzzy"])
        self.match_type_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.match_type_filter)
        
        # Clear filters button
        self.clear_filters_btn = QPushButton("Clear Filters")
        self.clear_filters_btn.clicked.connect(self._clear_filters)
        filter_layout.addWidget(self.clear_filters_btn)
        
        filter_layout.addStretch()
        parent_widget.layout().insertLayout(1, filter_layout)
        
    def load_keywords(self, keywords: List[Dict[str, Any]]) -> None:
        """
        Load a list of keyword dictionaries into the table.
        """
        self._original_data = keywords.copy()
        self._filtered_data = keywords.copy()
        
        # Update business filter options
        if hasattr(self, 'business_filter'):
            self._update_business_filter()
        
        self._populate_table()
        
    def _update_business_filter(self) -> None:
        """Update the business filter dropdown with current businesses."""
        if not hasattr(self, 'business_filter'):
            return
            
        current_text = self.business_filter.currentText()
        self.business_filter.clear()
        self.business_filter.addItem("All Businesses")
        
        businesses = sorted(list(set(
            kw.get('business_name', '') for kw in self._original_data 
            if kw.get('business_name')
        )))
        
        for business in businesses:
            self.business_filter.addItem(business)
            
        # Restore previous selection if it still exists
        if current_text and current_text in businesses:
            self.business_filter.setCurrentText(current_text)
            
    def _populate_table(self) -> None:
        """Populate the table with filtered data."""
        self.setSortingEnabled(False)  # Disable sorting during population
        self.setRowCount(0)
        
        for keyword in self._filtered_data:
            row = self.rowCount()
            self.insertRow(row)
            
            # Business name
            business_item = QTableWidgetItem(str(keyword.get("business_name", "")))
            business_item.setData(Qt.ItemDataRole.UserRole, keyword)
            self.setItem(row, 0, business_item)
            
            # Keyword
            keyword_item = QTableWidgetItem(str(keyword.get("keyword", "")))
            self.setItem(row, 1, keyword_item)
            
            # Match type (use the actual match_type field from database)
            match_type = keyword.get("match_type", "exact")
            match_item = QTableWidgetItem(match_type)
            self.setItem(row, 2, match_item)
            
            # Case sensitive
            case_sensitive = "Yes" if keyword.get("is_case_sensitive", 0) == 1 else "No"
            case_item = QTableWidgetItem(case_sensitive)
            self.setItem(row, 3, case_item)
            
            # Usage count
            usage_count = keyword.get("usage_count", 0)
            usage_item = QTableWidgetItem(str(usage_count))
            usage_item.setData(Qt.ItemDataRole.UserRole, usage_count)  # For proper sorting
            self.setItem(row, 4, usage_item)
            
            # Last used
            last_used = keyword.get("last_used", "")
            if last_used:
                try:
                    # Try to format the date nicely
                    if isinstance(last_used, str):
                        # Assuming last_used is a string, format it
                        last_used_display = last_used
                    else:
                        last_used_display = str(last_used)
                except:
                    last_used_display = str(last_used)
            else:
                last_used_display = "Never"
                
            last_used_item = QTableWidgetItem(last_used_display)
            last_used_item.setData(Qt.ItemDataRole.UserRole, last_used)  # Store original for sorting
            self.setItem(row, 5, last_used_item)
            
        self.setSortingEnabled(True)  # Re-enable sorting
        self.resizeColumnsToContents()
        
    def _apply_filters(self) -> None:
        """Apply all active filters to the data."""
        search_text = self.search_filter.text().lower() if hasattr(self, 'search_filter') else ""
        business_filter = self.business_filter.currentText() if hasattr(self, 'business_filter') else "All Businesses"
        match_type_filter = self.match_type_filter.currentText() if hasattr(self, 'match_type_filter') else "All Types"
        
        self._filtered_data = []
        
        for keyword in self._original_data:
            # Apply search filter
            if search_text:
                business_name = str(keyword.get("business_name", "")).lower()
                keyword_text = str(keyword.get("keyword", "")).lower()
                if search_text not in business_name and search_text not in keyword_text:
                    continue
                    
            # Apply business filter
            if business_filter != "All Businesses":
                if keyword.get("business_name", "") != business_filter:
                    continue
                    
            # Apply match type filter
            if match_type_filter != "All Types":
                is_case_sensitive = keyword.get("is_case_sensitive", 0) == 1
                keyword_match_type = "exact" if is_case_sensitive else "fuzzy"
                if keyword_match_type != match_type_filter:
                    continue
                    
            self._filtered_data.append(keyword)
            
        self._populate_table()
        
    def _clear_filters(self) -> None:
        """Clear all filters."""
        if hasattr(self, 'search_filter'):
            self.search_filter.clear()
        if hasattr(self, 'business_filter'):
            self.business_filter.setCurrentText("All Businesses")
        if hasattr(self, 'match_type_filter'):
            self.match_type_filter.setCurrentText("All Types")
            
        self._filtered_data = self._original_data.copy()
        self._populate_table()
        
    def _on_selection_changed(self) -> None:
        """Handle selection changes."""
        selected_rows = self.selectionModel().selectedRows()
        selected_keywords = []
        
        for index in selected_rows:
            row = index.row()
            if row < len(self._filtered_data):
                selected_keywords.append(self._filtered_data[row])
                
        self.selection_changed.emit(selected_keywords)
        
    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """Handle double-click on table item."""
        row = item.row()
        if row < len(self._filtered_data):
            keyword_data = self._filtered_data[row]
            self.keyword_double_clicked.emit(keyword_data)
            
    def get_selected_keywords(self) -> List[Dict[str, Any]]:
        """Get currently selected keywords."""
        selected_rows = self.selectionModel().selectedRows()
        selected_keywords = []
        
        for index in selected_rows:
            row = index.row()
            if row < len(self._filtered_data):
                selected_keywords.append(self._filtered_data[row])
                
        return selected_keywords
        
    def get_selected_keyword(self) -> Optional[Dict[str, Any]]:
        """Get the first selected keyword, or None if no selection."""
        selected = self.get_selected_keywords()
        return selected[0] if selected else None
        
    def select_keyword(self, keyword: str, business_name: str) -> bool:
        """Select a specific keyword in the table."""
        for row, kw_data in enumerate(self._filtered_data):
            if (kw_data.get("keyword") == keyword and 
                kw_data.get("business_name") == business_name):
                self.selectRow(row)
                return True
        return False
        
    def refresh(self) -> None:
        """Refresh the table display."""
        self._populate_table()
        
    def get_filter_widgets(self) -> Dict[str, QWidget]:
        """Get filter widgets for external setup."""
        return {
            'search_filter': getattr(self, 'search_filter', None),
            'business_filter': getattr(self, 'business_filter', None),
            'match_type_filter': getattr(self, 'match_type_filter', None),
            'clear_filters_btn': getattr(self, 'clear_filters_btn', None)
        }
        
    def contextMenuEvent(self, event) -> None:
        """Handle right-click context menu."""
        menu = QMenu(self)
        
        # Add actions based on selection
        selected_keywords = self.get_selected_keywords()
        
        if selected_keywords:
            edit_action = QAction("Edit Keyword", self)
            edit_action.triggered.connect(self._edit_selected_keyword)
            menu.addAction(edit_action)
            
            delete_action = QAction("Delete Keyword", self)
            delete_action.triggered.connect(self._delete_selected_keywords)
            menu.addAction(delete_action)
            
            menu.addSeparator()
            
        # Add general actions
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)
        
        clear_filters_action = QAction("Clear Filters", self)
        clear_filters_action.triggered.connect(self._clear_filters)
        menu.addAction(clear_filters_action)
        
        menu.exec(event.globalPos())
        
    def _edit_selected_keyword(self) -> None:
        """Edit the selected keyword (placeholder for now)."""
        selected = self.get_selected_keyword()
        if selected:
            self.keyword_selected.emit(selected)
            
    def _delete_selected_keywords(self) -> None:
        """Delete selected keywords (placeholder for now)."""
        selected = self.get_selected_keywords()
        if selected:
            count = len(selected)
            reply = QMessageBox.question(
                self, 
                "Delete Keywords", 
                f"Are you sure you want to delete {count} selected keyword(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Emit signal for parent to handle deletion
                for keyword in selected:
                    # This would typically emit a signal to the parent
                    pass 
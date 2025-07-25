from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QDialog
from ..business.business_mapping_manager import BusinessMappingManager
from .dialogs.add_business_dialog import AddBusinessDialog
from .widgets.keywords_table import KeywordsTable

class BusinessKeywordsTab(QWidget):
    """
    Business Keywords Tab for managing business keywords and statistics.
    """
    def __init__(self, business_mapping_manager: BusinessMappingManager, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.business_mapping_manager = business_mapping_manager
        self._setup_ui()
        self._setup_connections()
        self._load_keywords()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()
        self.add_button = QPushButton("Add Business")
        self.edit_button = QPushButton("Edit Keyword")
        self.delete_button = QPushButton("Delete Keyword")
        self.refresh_button = QPushButton("Refresh")
        
        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addWidget(self.refresh_button)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Keywords table with filters
        self.keywords_table = KeywordsTable()
        self.keywords_table._setup_filter_widgets(self)  # Add filter widgets
        layout.addWidget(self.keywords_table)

        # Statistics label
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)

    def _setup_connections(self) -> None:
        self.add_button.clicked.connect(self._on_add_business)
        self.edit_button.clicked.connect(self._on_edit_keyword)
        self.delete_button.clicked.connect(self._on_delete_keyword)
        self.refresh_button.clicked.connect(self._load_keywords)
        
        # Connect table signals
        self.keywords_table.keyword_selected.connect(self._on_keyword_selected)
        self.keywords_table.keyword_double_clicked.connect(self._on_keyword_double_clicked)
        self.keywords_table.selection_changed.connect(self._on_selection_changed)

    def _on_add_business(self) -> None:
        dialog = AddBusinessDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            business_name = dialog.get_business_name()
            if business_name:
                success = self.business_mapping_manager.add_business(business_name)
                if success:
                    self._load_keywords()
                else:
                    QMessageBox.warning(self, "Add Business Failed", f"Business '{business_name}' already exists or could not be added.")

    def _on_edit_keyword(self) -> None:
        selected_keyword = self.keywords_table.get_selected_keyword()
        if selected_keyword:
            # TODO: Implement EditKeywordDialog
            QMessageBox.information(self, "Edit Keyword", f"Edit functionality for keyword '{selected_keyword.get('keyword')}' will be implemented in T7.3")
        else:
            QMessageBox.information(self, "No Selection", "Please select a keyword to edit.")

    def _on_delete_keyword(self) -> None:
        selected_keywords = self.keywords_table.get_selected_keywords()
        if selected_keywords:
            count = len(selected_keywords)
            reply = QMessageBox.question(
                self, 
                "Delete Keywords", 
                f"Are you sure you want to delete {count} selected keyword(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # TODO: Implement keyword deletion
                QMessageBox.information(self, "Delete Keywords", f"Delete functionality for {count} keywords will be implemented in T7.3")
        else:
            QMessageBox.information(self, "No Selection", "Please select keywords to delete.")

    def _on_keyword_selected(self, keyword_data: dict) -> None:
        """Handle keyword selection."""
        # Update button states based on selection
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def _on_keyword_double_clicked(self, keyword_data: dict) -> None:
        """Handle keyword double-click."""
        # Same as edit for now
        self._on_edit_keyword()

    def _on_selection_changed(self, selected_keywords: list) -> None:
        """Handle selection changes."""
        has_selection = len(selected_keywords) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _load_keywords(self) -> None:
        keywords = self.business_mapping_manager.get_keywords()
        self.keywords_table.load_keywords(keywords)
        self._update_statistics(keywords)

    def _update_statistics(self, keywords) -> None:
        total_keywords = len(keywords)
        unique_businesses = len(set(k['business_name'] for k in keywords if 'business_name' in k))
        
        # Calculate additional statistics
        exact_matches = sum(1 for k in keywords if k.get('is_case_sensitive', 0) == 1)
        fuzzy_matches = total_keywords - exact_matches
        total_usage = sum(k.get('usage_count', 0) for k in keywords)
        
        stats_text = (
            f"Total Keywords: {total_keywords} | "
            f"Unique Businesses: {unique_businesses} | "
            f"Exact Matches: {exact_matches} | "
            f"Fuzzy Matches: {fuzzy_matches} | "
            f"Total Usage: {total_usage}"
        )
        self.stats_label.setText(stats_text) 
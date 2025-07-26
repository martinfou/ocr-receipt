from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QDialog, QSplitter, QTabWidget
from PyQt6.QtCore import Qt
from ..business.business_mapping_manager import BusinessMappingManager
from .dialogs.add_business_dialog import AddBusinessDialog
from .dialogs.edit_keyword_dialog import EditKeywordDialog
from .widgets.keywords_table import KeywordsTable
from .widgets.statistics_panel import StatisticsPanel
from ..utils.translation_helper import tr

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
        self._load_statistics()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()
        self.add_button = QPushButton(tr("business_keywords_tab.add_business"))
        self.edit_button = QPushButton(tr("business_keywords_tab.edit_keyword"))
        self.delete_button = QPushButton(tr("business_keywords_tab.delete_keyword"))
        self.refresh_button = QPushButton(tr("business_keywords_tab.refresh"))
        self.show_stats_button = QPushButton(tr("business_keywords_tab.show_statistics"))
        self.show_stats_button.setCheckable(True)
        self.show_stats_button.setChecked(True)
        
        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addWidget(self.refresh_button)
        toolbar.addStretch()
        toolbar.addWidget(self.show_stats_button)
        layout.addLayout(toolbar)

        # Main content area with splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)

        # Left side - Keywords table
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Keywords table with filters
        self.keywords_table = KeywordsTable()
        self.keywords_table._setup_filter_widgets(self)  # Add filter widgets
        left_layout.addWidget(self.keywords_table)
        
        # Simple statistics label (legacy)
        self.stats_label = QLabel()
        left_layout.addWidget(self.stats_label)
        
        self.splitter.addWidget(left_widget)

        # Right side - Statistics panel
        self.statistics_panel = StatisticsPanel()
        self.statistics_panel.refresh_button.clicked.connect(self._load_statistics)
        self.splitter.addWidget(self.statistics_panel)
        
        # Set initial splitter sizes (60% keywords, 40% statistics)
        self.splitter.setSizes([600, 400])

    def _setup_connections(self) -> None:
        self.add_button.clicked.connect(self._on_add_business)
        self.edit_button.clicked.connect(self._on_edit_keyword)
        self.delete_button.clicked.connect(self._on_delete_keyword)
        self.refresh_button.clicked.connect(self._load_keywords)
        self.show_stats_button.toggled.connect(self._toggle_statistics)
        
        # Connect table signals
        self.keywords_table.keyword_selected.connect(self._on_keyword_selected)
        self.keywords_table.keyword_double_clicked.connect(self._on_keyword_double_clicked)
        self.keywords_table.selection_changed.connect(self._on_selection_changed)

    def _toggle_statistics(self, show: bool) -> None:
        """Toggle the visibility of the statistics panel."""
        if show:
            self.statistics_panel.show()
            # Restore splitter sizes
            self.splitter.setSizes([600, 400])
        else:
            self.statistics_panel.hide()
            # Give all space to keywords table
            self.splitter.setSizes([1000, 0])

    def _on_add_business(self) -> None:
        dialog = AddBusinessDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            business_name = dialog.get_business_name()
            match_type = dialog.get_match_type()
            if business_name:
                success = self.business_mapping_manager.add_business(business_name, match_type=match_type)
                if success:
                    self._load_keywords()
                    self._load_statistics()  # Refresh statistics after adding business
                else:
                    QMessageBox.warning(self, tr("business_keywords_tab.add_business_failed"), 
                                       tr("business_keywords_tab.business_exists", business_name=business_name))

    def _on_edit_keyword(self) -> None:
        selected_keyword = self.keywords_table.get_selected_keyword()
        if selected_keyword:
            dialog = EditKeywordDialog(selected_keyword, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                edited_data = dialog.get_edited_data()
                if edited_data and dialog.has_changes():
                    # Check if business name changed
                    business_name_changed = edited_data['business_name'] != edited_data['original_business_name']
                    
                    if business_name_changed:
                        # Use the new method that handles both business name and keyword updates
                        success = self.business_mapping_manager.update_business_and_keyword(
                            edited_data['original_business_name'],
                            edited_data['business_name'],
                            edited_data['original_keyword'],
                            edited_data['keyword'],
                            edited_data['is_case_sensitive'],
                            edited_data['match_type']
                        )
                    else:
                        # Use the existing method for keyword-only updates
                        success = self.business_mapping_manager.update_keyword(
                            edited_data['business_name'],
                            edited_data['original_keyword'],
                            edited_data['keyword'],
                            edited_data['is_case_sensitive'],
                            edited_data['match_type']
                        )
                    
                    if success:
                        self._load_keywords()
                        self._load_statistics()  # Refresh statistics after editing
                        QMessageBox.information(self, tr("common.success"), tr("business_keywords_tab.keyword_updated"))
                    else:
                        if business_name_changed:
                            QMessageBox.warning(self, tr("common.error"), "Failed to update business name and keyword. The new business name may already exist.")
                        else:
                            QMessageBox.warning(self, tr("common.error"), tr("business_keywords_tab.update_failed"))
        else:
            QMessageBox.information(self, tr("common.information"), tr("business_keywords_tab.no_selection"))

    def _on_delete_keyword(self) -> None:
        selected_keywords = self.keywords_table.get_selected_keywords()
        if selected_keywords:
            count = len(selected_keywords)
            reply = QMessageBox.question(
                self, 
                tr("business_keywords_tab.delete_keywords"), 
                tr("business_keywords_tab.delete_confirm", count=count),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                success_count = 0
                failed_count = 0
                
                for keyword_data in selected_keywords:
                    success = self.business_mapping_manager.delete_keyword(
                        keyword_data['business_name'],
                        keyword_data['keyword']
                    )
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                
                self._load_keywords()
                self._load_statistics()  # Refresh statistics after deleting
                
                if failed_count == 0:
                    QMessageBox.information(self, tr("common.success"), 
                                          tr("business_keywords_tab.delete_success", success_count=success_count))
                elif success_count == 0:
                    QMessageBox.warning(self, tr("common.error"), 
                                      tr("business_keywords_tab.delete_failed", failed_count=failed_count))
                else:
                    QMessageBox.information(self, tr("common.information"), 
                                          tr("business_keywords_tab.delete_partial", 
                                             success_count=success_count, failed_count=failed_count))
        else:
            QMessageBox.information(self, tr("common.information"), tr("business_keywords_tab.no_selection_delete"))

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

    def _load_statistics(self) -> None:
        """Load comprehensive statistics from the business mapping manager."""
        try:
            stats = self.business_mapping_manager.get_comprehensive_statistics()
            self.statistics_panel.load_statistics(stats)
        except Exception as e:
            print(f"Error loading comprehensive statistics: {e}")

    def _update_statistics(self, keywords) -> None:
        total_keywords = len(keywords)
        unique_businesses = len(set(k['business_name'] for k in keywords if 'business_name' in k))
        
        # Calculate additional statistics
        exact_matches = sum(1 for k in keywords if k.get('is_case_sensitive', 0) == 1)
        fuzzy_matches = total_keywords - exact_matches
        total_usage = sum(k.get('usage_count', 0) for k in keywords)
        
        stats_text = (
            f"{tr('business_keywords_tab.total_keywords', total=total_keywords)} | "
            f"{tr('business_keywords_tab.unique_businesses', unique=unique_businesses)} | "
            f"{tr('business_keywords_tab.exact_matches', exact=exact_matches)} | "
            f"{tr('business_keywords_tab.fuzzy_matches', fuzzy=fuzzy_matches)} | "
            f"{tr('business_keywords_tab.total_usage', usage=total_usage)}"
        )
        self.stats_label.setText(stats_text)

    def update_language(self) -> None:
        """Update all text elements when language changes."""
        # Update button texts
        self.add_button.setText(tr("business_keywords_tab.add_business"))
        self.edit_button.setText(tr("business_keywords_tab.edit_keyword"))
        self.delete_button.setText(tr("business_keywords_tab.delete_keyword"))
        self.refresh_button.setText(tr("business_keywords_tab.refresh"))
        self.show_stats_button.setText(tr("business_keywords_tab.show_statistics"))
        
        # Update statistics if they exist
        if hasattr(self, 'stats_label') and self.stats_label.text():
            self._load_keywords()  # This will update the statistics 
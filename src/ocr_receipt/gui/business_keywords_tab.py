from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QDialog, QSplitter, QTabWidget, QFrame, QGroupBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..business.business_mapping_manager import BusinessMappingManager
from .dialogs.add_business_dialog import AddBusinessDialog
from .dialogs.edit_keyword_dialog import EditKeywordDialog
from .dialogs.add_keyword_dialog import AddKeywordDialog
from .widgets.keywords_table import KeywordsTable
from .widgets.statistics_panel import StatisticsPanel
from ..utils.translation_helper import tr
import logging

logger = logging.getLogger(__name__)

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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header section
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setMaximumHeight(60)  # Constrain header height to match other tabs
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(tr("business_keywords_tab.title"))
        title_label.setObjectName("title_label")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(tr("business_keywords_tab.subtitle"))
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setStyleSheet("color: #666;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)

        # Toolbar
        toolbar = QHBoxLayout()
        self.add_button = QPushButton(tr("business_keywords_tab.add_business"))
        self.add_keyword_button = QPushButton(tr("business_keywords_tab.add_keyword"))
        self.edit_button = QPushButton(tr("business_keywords_tab.edit_keyword"))
        self.delete_button = QPushButton(tr("business_keywords_tab.delete_keyword"))
        self.delete_business_button = QPushButton(tr("business_keywords_tab.delete_business"))
        self.refresh_button = QPushButton(tr("business_keywords_tab.refresh"))
        self.show_orphaned_button = QPushButton("Show Businesses Without Keywords")
        self.show_stats_button = QPushButton(tr("business_keywords_tab.show_statistics"))
        self.show_stats_button.setCheckable(True)
        self.show_stats_button.setChecked(True)
        
        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.add_keyword_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addWidget(self.delete_business_button)
        toolbar.addWidget(self.refresh_button)
        toolbar.addWidget(self.show_orphaned_button)
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
        
        # Orphaned businesses section
        self.orphaned_group = QGroupBox("Businesses Without Keywords")
        self.orphaned_group.setVisible(False)  # Hidden by default
        orphaned_layout = QVBoxLayout(self.orphaned_group)
        
        # Add delete button for orphaned businesses
        orphaned_buttons_layout = QHBoxLayout()
        self.delete_orphaned_button = QPushButton("Delete All Businesses Without Keywords")
        self.delete_orphaned_button.setStyleSheet("background-color: #ffcccc; color: #cc0000; font-weight: bold;")
        orphaned_buttons_layout.addWidget(self.delete_orphaned_button)
        orphaned_buttons_layout.addStretch()
        orphaned_layout.addLayout(orphaned_buttons_layout)
        
        self.orphaned_table = QLabel()
        self.orphaned_table.setWordWrap(True)
        self.orphaned_table.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        orphaned_layout.addWidget(self.orphaned_table)
        
        left_layout.addWidget(self.orphaned_group)
        
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
        self.add_keyword_button.clicked.connect(self._on_add_keyword)
        self.edit_button.clicked.connect(self._on_edit_keyword)
        self.delete_button.clicked.connect(self._on_delete_keyword)
        self.delete_business_button.clicked.connect(self._on_delete_business)
        self.refresh_button.clicked.connect(self._load_keywords)
        self.show_orphaned_button.clicked.connect(self._toggle_orphaned_businesses)
        self.delete_orphaned_button.clicked.connect(self._delete_orphaned_businesses)
        self.show_stats_button.toggled.connect(self._toggle_statistics)
        
        # Connect table signals
        self.keywords_table.keyword_selected.connect(self._on_keyword_selected)
        self.keywords_table.keyword_double_clicked.connect(self._on_keyword_double_clicked)
        self.keywords_table.selection_changed.connect(self._on_selection_changed)
        self.keywords_table.keywords_deleted.connect(self._on_keywords_deleted)
        
        # Connect business mapping manager signals for automatic UI updates
        self.business_mapping_manager.keyword_deleted.connect(self._on_keyword_deleted_from_manager)
        self.business_mapping_manager.business_deleted.connect(self._on_business_deleted_from_manager)

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

    def _toggle_orphaned_businesses(self) -> None:
        """Toggle the visibility of the orphaned businesses section."""
        is_visible = self.orphaned_group.isVisible()
        if not is_visible:
            self._load_orphaned_businesses()
        self.orphaned_group.setVisible(not is_visible)
        
        # Update button text
        if not is_visible:
            self.show_orphaned_button.setText("Hide Businesses Without Keywords")
        else:
            self.show_orphaned_button.setText("Show Businesses Without Keywords")

    def _load_orphaned_businesses(self) -> None:
        """Load and display businesses that don't have any keywords."""
        try:
            # Get all businesses and keywords
            businesses = self.business_mapping_manager.get_business_names()
            keywords = self.business_mapping_manager.get_keywords()
            
            # Find businesses that don't have keywords
            businesses_with_keywords = set(k['business_name'] for k in keywords)
            orphaned_businesses = [b for b in businesses if b not in businesses_with_keywords]
            
            if orphaned_businesses:
                orphaned_text = f"Found {len(orphaned_businesses)} business(es) without keywords:\n\n"
                for i, business in enumerate(orphaned_businesses, 1):
                    orphaned_text += f"{i}. {business}\n"
                orphaned_text += f"\nThese businesses exist in the database but have no keywords for matching."
            else:
                orphaned_text = "All businesses have keywords. No orphaned businesses found."
            
            self.orphaned_table.setText(orphaned_text)
        except Exception as e:
            logger.error(f"Error loading orphaned businesses: {e}")
            self.orphaned_table.setText("Error loading orphaned businesses.")

    def _delete_orphaned_businesses(self) -> None:
        """Delete all businesses that don't have any keywords."""
        try:
            businesses_to_delete = self.business_mapping_manager.get_business_names()
            keywords = self.business_mapping_manager.get_keywords()
            
            businesses_with_keywords = set(k['business_name'] for k in keywords)
            businesses_to_delete = [b for b in businesses_to_delete if b not in businesses_with_keywords]
            
            if businesses_to_delete:
                count = len(businesses_to_delete)
                reply = QMessageBox.question(
                    self, 
                    "Delete Businesses Without Keywords", 
                    f"Are you sure you want to delete {count} business(es) that have no keywords?\n\nThis will permanently remove these businesses from the database.\nThis action cannot be undone.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    success_count = 0
                    failed_count = 0
                    
                    for business_name in businesses_to_delete:
                        success = self.business_mapping_manager.delete_business(business_name)
                        if success:
                            success_count += 1
                        else:
                            failed_count += 1
                    
                    if failed_count == 0:
                        QMessageBox.information(self, "Success", f"Successfully deleted {success_count} business(es) without keywords.")
                        self._load_keywords() # Refresh keywords to update orphaned count
                        self._load_statistics() # Refresh statistics
                        if self.orphaned_group.isVisible():
                            self._load_orphaned_businesses() # Refresh orphaned list
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to delete {failed_count} business(es).")
                else:
                    logger.info("User cancelled deletion of orphaned businesses.")
            else:
                QMessageBox.information(self, "Information", "No businesses without keywords found to delete.")
        except Exception as e:
            logger.error(f"Error deleting orphaned businesses: {e}")
            QMessageBox.warning(self, "Error", "An error occurred while deleting businesses without keywords.")

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

    def _on_add_keyword(self) -> None:
        """Handle adding a keyword to an existing business."""
        business_names = self.business_mapping_manager.get_business_names()
        if not business_names:
            QMessageBox.information(self, tr("common.information"), 
                                  tr("business_keywords_tab.no_businesses_to_add_keyword"))
            return
        
        dialog = AddKeywordDialog(business_names, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            business_name = dialog.get_business_name()
            keyword = dialog.get_keyword()
            is_case_sensitive = dialog.get_is_case_sensitive()
            match_type = dialog.get_match_type()
            
            if business_name and keyword:
                success = self.business_mapping_manager.add_keyword(
                    business_name, 
                    keyword, 
                    is_case_sensitive=1 if is_case_sensitive else 0,
                    match_type=match_type
                )
                if success:
                    self._load_keywords()
                    self._load_statistics()  # Refresh statistics after adding keyword
                    QMessageBox.information(self, tr("common.success"), 
                                          tr("business_keywords_tab.keyword_added_success"))
                else:
                    QMessageBox.warning(self, tr("common.error"), 
                                      tr("business_keywords_tab.keyword_added_failed"))

    def _on_delete_business(self) -> None:
        """Handle deleting a business and all its keywords."""
        selected_keywords = self.keywords_table.get_selected_keywords()
        if not selected_keywords:
            QMessageBox.information(self, tr("common.information"), 
                                  tr("business_keywords_tab.no_selection_delete_business"))
            return
        
        # Get unique businesses from selected keywords
        businesses_to_delete = list(set(kw['business_name'] for kw in selected_keywords))
        
        if len(businesses_to_delete) == 1:
            business_name = businesses_to_delete[0]
            keyword_count = self.business_mapping_manager.get_keyword_count_for_business(business_name)
            reply = QMessageBox.question(
                self,
                tr("business_keywords_tab.delete_business"),
                tr("business_keywords_tab.delete_business_confirm", 
                   business_name=business_name, keyword_count=keyword_count),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                success = self.business_mapping_manager.delete_business(business_name)
                if success:
                    QMessageBox.information(self, tr("common.success"), 
                                          tr("business_keywords_tab.business_deleted_success"))
                else:
                    QMessageBox.warning(self, tr("common.error"), 
                                      tr("business_keywords_tab.business_deleted_failed"))
        else:
            # Multiple businesses selected
            business_list = ", ".join(businesses_to_delete)
            reply = QMessageBox.question(
                self,
                tr("business_keywords_tab.delete_businesses"),
                tr("business_keywords_tab.delete_businesses_confirm", 
                   business_list=business_list, count=len(businesses_to_delete)),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                success_count = 0
                failed_count = 0
                
                for business_name in businesses_to_delete:
                    success = self.business_mapping_manager.delete_business(business_name)
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                
                if failed_count == 0:
                    QMessageBox.information(self, tr("common.success"), 
                                          tr("business_keywords_tab.businesses_deleted_success", 
                                             success_count=success_count))
                elif success_count == 0:
                    QMessageBox.warning(self, tr("common.error"), 
                                      tr("business_keywords_tab.businesses_deleted_failed", 
                                         failed_count=failed_count))
                else:
                    QMessageBox.information(self, tr("common.information"), 
                                          tr("business_keywords_tab.businesses_deleted_partial", 
                                             success_count=success_count, failed_count=failed_count))

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
                        # Remove manual refresh - let signals handle it
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
            # Check if any of the selected keywords are the last keyword for their business
            last_keyword_businesses = []
            for keyword_data in selected_keywords:
                if self.business_mapping_manager.is_last_keyword_for_business(
                    keyword_data['business_name'], 
                    keyword_data['keyword']
                ):
                    last_keyword_businesses.append(keyword_data['business_name'])
            
            # If any keywords are the last for their business, show confirmation
            if last_keyword_businesses:
                business_list = ", ".join(last_keyword_businesses)
                reply = QMessageBox.question(
                    self,
                    tr("business_keywords_tab.delete_last_keyword"),
                    tr("business_keywords_tab.delete_last_keyword_confirm", 
                       business_list=business_list),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Proceed with deletion
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
                businesses_to_delete = set()  # Track businesses that need to be deleted
                
                for keyword_data in selected_keywords:
                    success = self.business_mapping_manager.delete_keyword(
                        keyword_data['business_name'],
                        keyword_data['keyword']
                    )
                    if success:
                        success_count += 1
                        # If this was the last keyword for the business, mark it for deletion
                        if keyword_data['business_name'] in last_keyword_businesses:
                            businesses_to_delete.add(keyword_data['business_name'])
                    else:
                        failed_count += 1
                
                # Delete businesses that had their last keyword removed
                for business_name in businesses_to_delete:
                    self.business_mapping_manager.delete_business(business_name)
                
                # Remove manual refresh - let signals handle it
                
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

    def _on_keywords_deleted(self, selected_keywords: list) -> None:
        """Handle keywords deletion from context menu."""
        if selected_keywords:
            # Check if any of the selected keywords are the last keyword for their business
            last_keyword_businesses = []
            for keyword_data in selected_keywords:
                if self.business_mapping_manager.is_last_keyword_for_business(
                    keyword_data['business_name'], 
                    keyword_data['keyword']
                ):
                    last_keyword_businesses.append(keyword_data['business_name'])
            
            # If any keywords are the last for their business, show confirmation
            if last_keyword_businesses:
                business_list = ", ".join(last_keyword_businesses)
                reply = QMessageBox.question(
                    self,
                    tr("business_keywords_tab.delete_last_keyword"),
                    tr("business_keywords_tab.delete_last_keyword_confirm", 
                       business_list=business_list),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            success_count = 0
            failed_count = 0
            businesses_to_delete = set()  # Track businesses that need to be deleted
            
            for keyword_data in selected_keywords:
                success = self.business_mapping_manager.delete_keyword(
                    keyword_data['business_name'],
                    keyword_data['keyword']
                )
                if success:
                    success_count += 1
                    # If this was the last keyword for the business, mark it for deletion
                    if keyword_data['business_name'] in last_keyword_businesses:
                        businesses_to_delete.add(keyword_data['business_name'])
                else:
                    failed_count += 1
            
            # Delete businesses that had their last keyword removed
            for business_name in businesses_to_delete:
                self.business_mapping_manager.delete_business(business_name)
            
            # Refresh the table and statistics
            self._load_keywords()
            self._load_statistics()
            
            # Show appropriate message
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

    def _on_keyword_deleted_from_manager(self, business_name: str, keyword: str) -> None:
        """Handle keyword deletion signal from business mapping manager."""
        # Refresh the table and statistics when keywords are deleted from other sources
        self._load_keywords()
        self._load_statistics()

    def _on_business_deleted_from_manager(self, business_name: str) -> None:
        """Handle business deletion signal from business mapping manager."""
        # Refresh the table and statistics when businesses are deleted
        self._load_keywords()
        self._load_statistics()

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
            logger.error(f"Error loading comprehensive statistics: {e}")

    def refresh_keywords(self) -> None:
        """Refresh the keywords table and statistics when data changes."""
        try:
            self._load_keywords()
            self._load_statistics()
        except Exception as e:
            logger.error(f"Error refreshing keywords: {e}")

    def _update_statistics(self, keywords) -> None:
        # Defensive check for mock objects or invalid data
        if not isinstance(keywords, list):
            logger.error(f"Expected list for keywords, got {type(keywords)}")
            self.stats_label.setText("Error: Invalid keyword data")
            return
            
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
        self.add_keyword_button.setText(tr("business_keywords_tab.add_keyword"))
        self.edit_button.setText(tr("business_keywords_tab.edit_keyword"))
        self.delete_button.setText(tr("business_keywords_tab.delete_keyword"))
        self.delete_business_button.setText(tr("business_keywords_tab.delete_business"))
        self.refresh_button.setText(tr("business_keywords_tab.refresh"))
        self.show_stats_button.setText(tr("business_keywords_tab.show_statistics"))
        
        # Update title and subtitle
        title_label = self.findChild(QLabel, "title_label")
        if title_label:
            title_label.setText(tr("business_keywords_tab.title"))
        
        subtitle_label = self.findChild(QLabel, "subtitle_label")
        if subtitle_label:
            subtitle_label.setText(tr("business_keywords_tab.subtitle"))
        
        # Update statistics if they exist
        if hasattr(self, 'stats_label') and self.stats_label.text():
            self._load_keywords()  # This will update the statistics 
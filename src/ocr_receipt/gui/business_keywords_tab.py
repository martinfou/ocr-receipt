from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QDialog
from ..business.business_mapping_manager import BusinessMappingManager
from .dialogs.add_business_dialog import AddBusinessDialog
# Import KeywordsTable if available, otherwise use a placeholder
try:
    from .widgets.keywords_table import KeywordsTable
except ImportError:
    class KeywordsTable(QWidget):
        def load_keywords(self, keywords):
            pass

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
        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Keywords table
        self.keywords_table = KeywordsTable()
        layout.addWidget(self.keywords_table)

        # Statistics label
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)

    def _setup_connections(self) -> None:
        self.add_button.clicked.connect(self._on_add_business)
        # TODO: Connect edit and delete buttons

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

    def _load_keywords(self) -> None:
        keywords = self.business_mapping_manager.get_keywords()
        self.keywords_table.load_keywords(keywords)
        self._update_statistics(keywords)

    def _update_statistics(self, keywords) -> None:
        total_keywords = len(keywords)
        unique_businesses = len(set(k['business_name'] for k in keywords if 'business_name' in k))
        self.stats_label.setText(f"Total Keywords: {total_keywords} | Unique Businesses: {unique_businesses}") 
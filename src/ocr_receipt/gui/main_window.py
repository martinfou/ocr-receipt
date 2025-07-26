from PyQt6.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from ocr_receipt.config import ConfigManager
from .single_pdf_tab import SinglePDFTab
from .business_keywords_tab import BusinessKeywordsTab
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
from ocr_receipt.business.project_manager import ProjectManager
from ocr_receipt.business.category_manager import CategoryManager
from ocr_receipt.utils.translation_helper import set_language, tr

class OCRMainWindow(QMainWindow):
    """Main application window for OCR Invoice Parser."""
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        
        # Initialize translation system
        self._init_translations()
        
        # Instantiate database and business logic managers
        db_path = self.config_manager.get('database.path', 'ocr_receipts.db')
        self.db_manager = DatabaseManager(db_path)
        self.business_mapping_manager = BusinessMappingManager(self.db_manager)
        self.project_manager = ProjectManager(self.db_manager)
        self.category_manager = CategoryManager(self.db_manager)
        self._setup_ui()

    def _init_translations(self):
        """Initialize the translation system."""
        # Get language from config
        language = self.config_manager.get('app.ui_language', 'en')
        set_language(language)

    def _setup_ui(self):
        self.setWindowTitle(tr("main_window.title"))
        window_size = self.config_manager.get('gui.window_size', [1200, 800])
        self.resize(*window_size)
        self.setMinimumSize(800, 600)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Add main tabs, passing business logic managers to SinglePDFTab
        self.tab_widget.addTab(
            SinglePDFTab(
                business_mapping_manager=self.business_mapping_manager,
                project_manager=self.project_manager,
                category_manager=self.category_manager
            ),
            "Single PDF"
        )
        self.tab_widget.addTab(
            BusinessKeywordsTab(self.business_mapping_manager),
            "Business Keywords"
        )
        self._add_tab("Projects", "Projects Tab")
        self._add_tab("Categories", "Categories Tab")
        self._add_tab("File Naming", "File Naming Tab")
        self._add_tab("Settings", "Settings Tab")

    def _add_tab(self, name: str, label: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(label))
        self.tab_widget.addTab(widget, name)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = OCRMainWindow()
    window.show()
    sys.exit(app.exec()) 
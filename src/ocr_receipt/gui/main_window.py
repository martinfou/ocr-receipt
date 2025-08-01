from PyQt6.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from ocr_receipt.config import ConfigManager
from .single_pdf_tab import SinglePDFTab
from .business_keywords_tab import BusinessKeywordsTab
from .projects_tab import ProjectsTab
from .categories_tab import CategoriesTab
from .document_types_tab import DocumentTypesTab
from .file_naming_tab import FileNamingTab
from .settings_tab import SettingsTab
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
from ocr_receipt.business.project_manager import ProjectManager
from ocr_receipt.business.category_manager import CategoryManager
from ocr_receipt.business.document_type_manager import DocumentTypeManager
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
        self.document_type_manager = DocumentTypeManager(self.db_manager)
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
        self.single_pdf_tab = SinglePDFTab(
            business_mapping_manager=self.business_mapping_manager,
            project_manager=self.project_manager,
            category_manager=self.category_manager,
            document_type_manager=self.document_type_manager,
            config_manager=self.config_manager
        )
        self.tab_widget.addTab(self.single_pdf_tab, tr("single_pdf_tab.title"))
        
        self.business_keywords_tab = BusinessKeywordsTab(self.business_mapping_manager)
        self.tab_widget.addTab(self.business_keywords_tab, tr("business_keywords_tab.title"))
        
        # Connect business mapping manager signals to refresh business keywords tab
        self.business_mapping_manager.business_added.connect(self._on_business_changed)
        self.business_mapping_manager.business_updated.connect(self._on_business_changed)
        self.business_mapping_manager.business_deleted.connect(self._on_business_changed)
        self.business_mapping_manager.keyword_added.connect(self._on_business_changed)
        self.business_mapping_manager.keyword_updated.connect(self._on_business_changed)
        self.business_mapping_manager.keyword_deleted.connect(self._on_business_changed)
        
        self.projects_tab = ProjectsTab(self.project_manager)
        self.projects_tab.projects_changed.connect(self._on_projects_changed)
        self.tab_widget.addTab(self.projects_tab, tr("projects_tab.title"))
        
        self.categories_tab = CategoriesTab(self.category_manager)
        self.categories_tab.categories_changed.connect(self._on_categories_changed)
        self.tab_widget.addTab(self.categories_tab, tr("categories_tab.title"))
        
        self.document_types_tab = DocumentTypesTab(self.document_type_manager)
        self.document_types_tab.document_types_changed.connect(self._on_document_types_changed)
        self.tab_widget.addTab(self.document_types_tab, tr("document_types_tab.title"))
        
        self.file_naming_tab = FileNamingTab(self.config_manager, self.document_type_manager)
        self.file_naming_tab.template_changed.connect(self._on_template_changed)
        self.tab_widget.addTab(self.file_naming_tab, tr("file_naming_tab.title"))
        
        # Create settings tab with language change signal connection
        self.settings_tab = SettingsTab(self.config_manager)
        self.settings_tab.language_changed.connect(self._on_language_changed)
        self.tab_widget.addTab(self.settings_tab, tr("settings_tab.title"))

    def _add_tab(self, name: str, label: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(label))
        self.tab_widget.addTab(widget, name)

    def _on_language_changed(self, new_language: str) -> None:
        """Handle language change from settings tab."""
        # Update window title
        self.setWindowTitle(tr("main_window.title"))
        
        # Update tab names
        self.tab_widget.setTabText(0, tr("single_pdf_tab.title"))
        self.tab_widget.setTabText(1, tr("business_keywords_tab.title"))
        self.tab_widget.setTabText(2, tr("projects_tab.title"))
        self.tab_widget.setTabText(3, tr("categories_tab.title"))
        self.tab_widget.setTabText(4, tr("document_types_tab.title"))
        self.tab_widget.setTabText(5, tr("file_naming_tab.title"))
        self.tab_widget.setTabText(6, tr("settings_tab.title"))
        
        # Update ProjectsTab button texts
        if hasattr(self, 'projects_tab'):
            self.projects_tab.update_language()
        
        # Update BusinessKeywordsTab button texts
        if hasattr(self, 'business_keywords_tab'):
            self.business_keywords_tab.update_language()
        
        # Update CategoriesTab button texts
        if hasattr(self, 'categories_tab'):
            self.categories_tab.update_language()
        
        # Update FileNamingTab button texts
        if hasattr(self, 'file_naming_tab'):
            self.file_naming_tab.update_language()

    def _on_categories_changed(self) -> None:
        """Handle category changes from CategoriesTab."""
        # Update Single PDF tab category dropdown
        if hasattr(self, 'single_pdf_tab'):
            self.single_pdf_tab.refresh_categories()
    
    def _on_document_types_changed(self) -> None:
        """Handle document types changes from DocumentTypesTab."""
        # Update Single PDF tab document type dropdown
        if hasattr(self, 'single_pdf_tab'):
            self.single_pdf_tab.refresh_document_types()

    def _on_projects_changed(self) -> None:
        """Handle project changes from ProjectsTab."""
        # Update Single PDF tab project dropdown
        if hasattr(self, 'single_pdf_tab'):
            self.single_pdf_tab.refresh_projects()

    def _on_template_changed(self, template: str) -> None:
        """Handle template changes from FileNamingTab."""
        # Update Single PDF tab filename preview
        if hasattr(self, 'single_pdf_tab'):
            self.single_pdf_tab.refresh_templates()

    def _on_business_changed(self) -> None:
        """Handle business or keyword changes from BusinessMappingManager."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Business change detected - refreshing UI components")
        
        if hasattr(self, 'business_keywords_tab'):
            logger.info("Refreshing business keywords tab")
            self.business_keywords_tab.refresh_keywords()
        if hasattr(self, 'single_pdf_tab'):
            logger.info("Refreshing single PDF tab company dropdown")
            self.single_pdf_tab.refresh_company_dropdown()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = OCRMainWindow()
    window.show()
    sys.exit(app.exec()) 
from PyQt6.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from ocr_receipt.config import ConfigManager
from .single_pdf_tab import SinglePDFTab

class OCRMainWindow(QMainWindow):
    """Main application window for OCR Invoice Parser."""
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("OCR Invoice Parser")
        window_size = self.config_manager.get('gui.window_size', [1200, 800])
        self.resize(*window_size)
        self.setMinimumSize(800, 600)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Add main tabs
        self.tab_widget.addTab(SinglePDFTab(), "Single PDF")
        self._add_tab("Business Keywords", "Business Keywords Tab")
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
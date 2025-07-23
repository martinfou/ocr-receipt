from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import Qt
from ocr_receipt.config import ConfigManager

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
        # Placeholder: Add more UI setup here as needed

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = OCRMainWindow()
    window.show()
    sys.exit(app.exec()) 
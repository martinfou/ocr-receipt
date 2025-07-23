from PyQt6.QtWidgets import QApplication
from ocr_receipt.gui.main_window import OCRMainWindow
import sys

def main():
    app = QApplication(sys.argv)
    window = OCRMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
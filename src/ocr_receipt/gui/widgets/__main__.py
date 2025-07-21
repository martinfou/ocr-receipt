from PyQt6.QtWidgets import QApplication
from minimal_widget import MinimalWidget
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MinimalWidget("Test Widget")
    widget.show()
    sys.exit(app.exec()) 
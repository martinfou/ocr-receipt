from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class MinimalWidget(QWidget):
    """
    A minimal PyQt6 widget for testing purposes.
    """
    def __init__(self, text: str = "Hello, World!", parent=None):
        super().__init__(parent)
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_text(self, text: str) -> None:
        self.label.setText(text)

    def get_text(self) -> str:
        return self.label.text() 
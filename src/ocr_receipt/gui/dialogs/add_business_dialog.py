from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from typing import Optional

class AddBusinessDialog(QDialog):
    """
    Dialog for adding a new business name.
    """
    def __init__(self, parent: Optional[QDialog] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Business")
        self.setModal(True)
        self.business_name: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Business Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def accept(self) -> None:
        name = self.name_edit.text().strip()
        if name:
            self.business_name = name
            super().accept()
        else:
            self.name_edit.setFocus()
            self.name_edit.setPlaceholderText("Please enter a business name.")

    def get_business_name(self) -> Optional[str]:
        return self.business_name 
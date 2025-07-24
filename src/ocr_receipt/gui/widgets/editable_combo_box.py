from PyQt6.QtWidgets import QComboBox

class EditableComboBox(QComboBox):
    """A combo box that allows both selection and free text entry."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)

    def set_items(self, items):
        self.clear()
        self.addItems(items)

    def get_value(self):
        return self.currentText() 
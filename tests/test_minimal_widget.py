import pytest
from PyQt6.QtWidgets import QApplication
from ocr_receipt.gui.main_window import OCRMainWindow
from ocr_receipt.gui.widgets.data_panel import DataPanel
from ocr_receipt.gui.widgets.editable_combo_box import EditableComboBox

@pytest.fixture
def app(qtbot):
    return QApplication.instance() or QApplication([])

def test_main_window_launch(qtbot, app):
    window = OCRMainWindow()
    qtbot.addWidget(window)
    # window.show()  # Removed to prevent popup during testing
    assert window.windowTitle() == "OCR Invoice Parser"
    # assert window.isVisible()  # This assertion is no longer valid without show()

def test_main_window_tabs(qtbot, app):
    window = OCRMainWindow()
    qtbot.addWidget(window)
    expected_tabs = [
        "Single PDF",
        "Business Keywords",
        "Projects",
        "Categories",
        "File Naming",
        "Settings"
    ]
    actual_tabs = [window.tab_widget.tabText(i) for i in range(window.tab_widget.count())]
    for tab in expected_tabs:
        assert tab in actual_tabs

def test_data_panel_fields(qtbot, app):
    panel = DataPanel()
    qtbot.addWidget(panel)
    data = {
        "company": "TestCo",
        "total": 123.45,
        "date": "2024-07-01",
        "invoice_number": "INV-001"
    }
    panel.load_data(data)
    assert panel.company_edit.text() == "TestCo"
    assert panel.total_edit.text() == "123.45"
    assert panel.date_edit.text() == "2024-07-01"
    assert panel.invoice_number_edit.text() == "INV-001"

    # Simulate user editing fields
    panel.company_edit.setText("NewCo")
    panel.total_edit.setText("999.99")
    panel.date_edit.setText("2024-12-31")
    panel.invoice_number_edit.setText("INV-999")
    assert panel.company_edit.text() == "NewCo"
    assert panel.total_edit.text() == "999.99"
    assert panel.date_edit.text() == "2024-12-31"
    assert panel.invoice_number_edit.text() == "INV-999"

def test_editable_combo_box(qtbot, app):
    combo = EditableComboBox()
    qtbot.addWidget(combo)
    combo.set_items(["A", "B", "C"])
    combo.setCurrentIndex(1)
    assert combo.get_value() == "B"
    combo.setEditText("Custom")
    assert combo.get_value() == "Custom"
    # Simulate user clearing the field
    combo.setEditText("")
    assert combo.get_value() == ""
    # Simulate error: set_items with empty list
    combo.set_items([])
    assert combo.count() == 0 
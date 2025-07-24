import pytest
from PyQt6.QtWidgets import QApplication
from ocr_receipt.gui.widgets.minimal_widget import MinimalWidget
from ocr_receipt.gui.main_window import OCRMainWindow

@pytest.fixture
def widget(qtbot):
    w = MinimalWidget("Initial Text")
    qtbot.addWidget(w)
    return w

@pytest.fixture
def app(qtbot):
    return QApplication.instance() or QApplication([])

def test_initial_text(widget):
    assert widget.get_text() == "Initial Text"

def test_set_text(widget):
    widget.set_text("Updated Text")
    assert widget.get_text() == "Updated Text"

def test_main_window_launch(qtbot, app):
    window = OCRMainWindow()
    qtbot.addWidget(window)
    window.show()
    assert window.windowTitle() == "OCR Invoice Parser"
    assert window.isVisible()


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
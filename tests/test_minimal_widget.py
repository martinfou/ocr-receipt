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
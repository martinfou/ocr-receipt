import pytest
from PyQt6.QtWidgets import QApplication
from ocr_receipt.gui.widgets.minimal_widget import MinimalWidget

@pytest.fixture
def widget(qtbot):
    w = MinimalWidget("Initial Text")
    qtbot.addWidget(w)
    return w

def test_initial_text(widget):
    assert widget.get_text() == "Initial Text"

def test_set_text(widget):
    widget.set_text("Updated Text")
    assert widget.get_text() == "Updated Text" 
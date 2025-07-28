import pytest
from PyQt6.QtWidgets import QApplication
import sys

@pytest.fixture(scope="session")
def qapp():
    """
    Session-scoped fixture to create a single QApplication instance for the entire test run.
    This prevents resource leaks and segmentation faults when running many tests.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()

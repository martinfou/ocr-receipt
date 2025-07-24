import pytest
from PyQt6.QtWidgets import QApplication
from ocr_receipt.gui.single_pdf_tab import SinglePDFTab
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
from ocr_receipt.business.project_manager import ProjectManager
from ocr_receipt.business.category_manager import CategoryManager

@pytest.fixture
def app(qtbot):
    return QApplication.instance() or QApplication([])

@pytest.fixture
def single_pdf_tab(tmp_path, qtbot, app):
    # Use an in-memory SQLite DB for isolation
    db_manager = DatabaseManager(":memory:")
    # Create minimal schema for required tables
    db_manager.execute_query("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        );
    """)
    db_manager.execute_query("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            category_code TEXT
        );
    """)
    business_mapping_manager = BusinessMappingManager(db_manager)
    project_manager = ProjectManager(db_manager)
    category_manager = CategoryManager(db_manager)
    tab = SinglePDFTab(
        business_mapping_manager=business_mapping_manager,
        project_manager=project_manager,
        category_manager=category_manager
    )
    qtbot.addWidget(tab)
    return tab

def test_single_pdf_tab_instantiates(single_pdf_tab):
    assert single_pdf_tab is not None
    assert single_pdf_tab.file_path_edit is not None
    assert single_pdf_tab.pdf_preview is not None
    assert single_pdf_tab.data_panel is not None

def test_file_path_editable(single_pdf_tab, qtbot):
    single_pdf_tab.file_path_edit.setText("/fake/path/to/invoice.pdf")
    assert single_pdf_tab.file_path_edit.text() == "/fake/path/to/invoice.pdf"

def test_data_panel_fields_editable(single_pdf_tab, qtbot):
    panel = single_pdf_tab.data_panel
    panel.company_edit.setText("TestCo")
    panel.total_edit.setText("123.45")
    panel.date_edit.setText("2024-07-01")
    panel.invoice_number_edit.setText("INV-001")
    assert panel.company_edit.text() == "TestCo"
    assert panel.total_edit.text() == "123.45"
    assert panel.date_edit.text() == "2024-07-01"
    assert panel.invoice_number_edit.text() == "INV-001" 
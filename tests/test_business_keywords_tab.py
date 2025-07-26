import pytest
from ocr_receipt.gui.business_keywords_tab import BusinessKeywordsTab
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
import tempfile
import os

@pytest.fixture
def temp_db():
    db_fd, db_path = tempfile.mkstemp()
    db = DatabaseManager(db_path)
    db.connect()
    db.execute_query('''CREATE TABLE businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )''')
    db.execute_query('''CREATE TABLE business_keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id INTEGER NOT NULL,
        keyword TEXT NOT NULL,
        is_case_sensitive BOOLEAN DEFAULT 0,
        match_type TEXT NOT NULL DEFAULT 'exact',
        last_used TIMESTAMP,
        usage_count INTEGER DEFAULT 0,
        FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
    )''')
    yield db
    db.close()
    os.close(db_fd)
    os.remove(db_path)

@pytest.fixture
def manager(temp_db):
    return BusinessMappingManager(temp_db)

@pytest.fixture
def tab(qtbot, manager):
    widget = BusinessKeywordsTab(manager)
    qtbot.addWidget(widget)
    return widget

def test_add_business_updates_table(tab, qtbot):
    # Simulate adding a business
    initial_count = tab.keywords_table.rowCount()
    tab.business_mapping_manager.add_business("TestBiz")
    tab._load_keywords()
    assert tab.keywords_table.rowCount() == initial_count + 1
    # Check that the business name appears in the table
    found = False
    for row in range(tab.keywords_table.rowCount()):
        if tab.keywords_table.item(row, 0).text() == "TestBiz":
            found = True
    assert found

def test_add_duplicate_business_shows_error(tab, qtbot):
    # Add a business
    tab.business_mapping_manager.add_business("DupBiz")
    tab._load_keywords()
    # Try to add the same business again
    result = tab.business_mapping_manager.add_business("DupBiz")
    assert result is False
    # Table should not add a duplicate row
    count = 0
    for row in range(tab.keywords_table.rowCount()):
        if tab.keywords_table.item(row, 0).text() == "DupBiz":
            count += 1
    assert count == 1 
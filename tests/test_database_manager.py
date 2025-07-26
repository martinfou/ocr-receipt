import pytest
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.project_manager import ProjectManager
from ocr_receipt.business.category_manager import CategoryManager
from ocr_receipt.business.pdf_metadata_manager import PDFMetadataManager
import sqlite3
import tempfile
import os

@pytest.fixture
def db_manager():
    db = DatabaseManager(":memory:")
    db.connect()
    db.connection.execute("PRAGMA foreign_keys = ON")
    db.execute_query("""
        CREATE TABLE businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute_query("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute_query("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_code TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    yield db
    db.close()

@pytest.fixture
def project_manager(db_manager):
    return ProjectManager(db_manager)

@pytest.fixture
def category_manager(db_manager):
    return CategoryManager(db_manager)

@pytest.fixture
def pdf_metadata_manager(db_manager):
    db_manager.execute_query("""
        CREATE TABLE invoice_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            business TEXT,
            total REAL,
            date TEXT,
            invoice_number TEXT,
            check_number TEXT,
            raw_text TEXT,
            parser_type TEXT,
            confidence REAL,
            is_valid BOOLEAN DEFAULT FALSE,
            project_id INTEGER,
            category_id INTEGER,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
    """)
    return PDFMetadataManager(db_manager)

def setup_test_db():
    # Create a temporary SQLite database and required tables
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
    return db, db_fd, db_path

def teardown_test_db(db, db_fd, db_path):
    db.close()
    os.close(db_fd)
    os.remove(db_path)

def test_get_all_keywords():
    db, db_fd, db_path = setup_test_db()
    try:
        # Insert a business and a keyword
        db.execute_query("INSERT INTO businesses (name) VALUES (?)", ("TestCo",))
        business_id = db.execute_query("SELECT id FROM businesses WHERE name=?", ("TestCo",)).fetchone()[0]
        db.execute_query("INSERT INTO business_keywords (business_id, keyword, is_case_sensitive, match_type, usage_count) VALUES (?, ?, ?, ?, ?)", (business_id, "testkey", 1, "exact", 5))
        # Test get_all_keywords
        keywords = db.get_all_keywords()
        assert isinstance(keywords, list)
        assert len(keywords) == 1
        k = keywords[0]
        assert k["business_name"] == "TestCo"
        assert k["keyword"] == "testkey"
        assert k["is_case_sensitive"] == 1
        assert k["usage_count"] == 5
    finally:
        teardown_test_db(db, db_fd, db_path)

def test_create_project(project_manager):
    project_id = project_manager.create_project("Test Project", "A test project.")
    project = project_manager.get_project_by_id(project_id)
    assert project is not None
    assert project["name"] == "Test Project"
    assert project["description"] == "A test project."

def test_create_project_duplicate_name(project_manager):
    project_manager.create_project("Unique Project")
    with pytest.raises(ValueError):
        project_manager.create_project("Unique Project")

def test_create_project_empty_name(project_manager):
    with pytest.raises(ValueError):
        project_manager.create_project("")

def test_get_project_by_name(project_manager):
    project_manager.create_project("FindMe", "desc")
    project = project_manager.get_project_by_name("FindMe")
    assert project is not None
    assert project["name"] == "FindMe"

def test_list_projects(project_manager):
    project_manager.create_project("A")
    project_manager.create_project("B")
    projects = project_manager.list_projects()
    assert len(projects) == 2
    names = [p["name"] for p in projects]
    assert "A" in names and "B" in names

def test_update_project(project_manager):
    pid = project_manager.create_project("OldName", "desc")
    project_manager.update_project(pid, name="NewName", description="newdesc")
    project = project_manager.get_project_by_id(pid)
    assert project["name"] == "NewName"
    assert project["description"] == "newdesc"

def test_update_project_no_fields(project_manager):
    pid = project_manager.create_project("NoUpdate")
    with pytest.raises(ValueError):
        project_manager.update_project(pid)

def test_update_project_not_exist(project_manager):
    with pytest.raises(ValueError):
        project_manager.update_project(999, name="X")

def test_delete_project(project_manager):
    pid = project_manager.create_project("ToDelete")
    project_manager.delete_project(pid)
    assert project_manager.get_project_by_id(pid) is None

def test_delete_project_not_exist(project_manager):
    with pytest.raises(ValueError):
        project_manager.delete_project(999)

def test_delete_project_referenced_by_metadata(db_manager, project_manager, pdf_metadata_manager):
    # Create a project and reference it in metadata
    pid = project_manager.create_project("RefProj")
    data = {"business": "Biz", "project_id": pid}
    mid = pdf_metadata_manager.create_metadata("/tmp/withproj.pdf", data)
    
    # Verify the metadata has the project_id
    metadata = pdf_metadata_manager.get_metadata_by_file_path("/tmp/withproj.pdf")
    assert metadata["project_id"] == pid
    
    # Delete the project (should set project_id to NULL due to ON DELETE SET NULL)
    project_manager.delete_project(pid)
    
    # Verify the metadata still exists but project_id is now NULL
    metadata = pdf_metadata_manager.get_metadata_by_file_path("/tmp/withproj.pdf")
    assert metadata is not None
    assert metadata["project_id"] is None

def test_create_category(category_manager):
    category_id = category_manager.create_category("Test Category", "A test category.", "C001")
    category = category_manager.get_category_by_id(category_id)
    assert category is not None
    assert category["name"] == "Test Category"
    assert category["description"] == "A test category."
    assert category["category_code"] == "C001"

def test_create_category_duplicate_name(category_manager):
    category_manager.create_category("Unique Category")
    with pytest.raises(ValueError):
        category_manager.create_category("Unique Category")

def test_create_category_empty_name(category_manager):
    with pytest.raises(ValueError):
        category_manager.create_category("")

def test_get_category_by_name(category_manager):
    category_manager.create_category("FindMe", "desc", "C002")
    category = category_manager.get_category_by_name("FindMe")
    assert category is not None
    assert category["name"] == "FindMe"
    assert category["category_code"] == "C002"

def test_list_categories(category_manager):
    category_manager.create_category("A")
    category_manager.create_category("B")
    categories = category_manager.list_categories()
    assert len(categories) == 2
    names = [c["name"] for c in categories]
    assert "A" in names and "B" in names

def test_update_category(category_manager):
    cid = category_manager.create_category("OldName", "desc", "C003")
    category_manager.update_category(cid, name="NewName", description="newdesc", category_code="C004")
    category = category_manager.get_category_by_id(cid)
    assert category["name"] == "NewName"
    assert category["description"] == "newdesc"
    assert category["category_code"] == "C004"

def test_update_category_no_fields(category_manager):
    cid = category_manager.create_category("NoUpdate")
    with pytest.raises(ValueError):
        category_manager.update_category(cid)

def test_update_category_not_exist(category_manager):
    with pytest.raises(ValueError):
        category_manager.update_category(999, name="X")

def test_delete_category(category_manager):
    cid = category_manager.create_category("ToDelete")
    category_manager.delete_category(cid)
    assert category_manager.get_category_by_id(cid) is None

def test_delete_category_not_exist(category_manager):
    with pytest.raises(ValueError):
        category_manager.delete_category(999)

def test_delete_category_referenced_by_metadata(db_manager, category_manager, pdf_metadata_manager):
    # Create a category and reference it in metadata
    cid = category_manager.create_category("RefCat")
    data = {"business": "Biz", "category_id": cid}
    mid = pdf_metadata_manager.create_metadata("/tmp/withcat.pdf", data)
    
    # Verify the metadata has the category_id
    metadata = pdf_metadata_manager.get_metadata_by_file_path("/tmp/withcat.pdf")
    assert metadata["category_id"] == cid
    
    # Delete the category (should set category_id to NULL due to ON DELETE SET NULL)
    category_manager.delete_category(cid)
    
    # Verify the metadata still exists but category_id is now NULL
    metadata = pdf_metadata_manager.get_metadata_by_file_path("/tmp/withcat.pdf")
    assert metadata is not None
    assert metadata["category_id"] is None

def test_create_metadata(pdf_metadata_manager):
    data = {"business": "TestCo", "total": 123.45, "date": "2024-06-01", "invoice_number": "INV-001"}
    metadata_id = pdf_metadata_manager.create_metadata("/tmp/test.pdf", data)
    metadata = pdf_metadata_manager.get_metadata_by_id(metadata_id)
    assert metadata is not None
    assert metadata["file_path"] == "/tmp/test.pdf"
    assert metadata["business"] == "TestCo"
    assert metadata["total"] == 123.45
    assert metadata["invoice_number"] == "INV-001"

def test_create_metadata_duplicate_file(pdf_metadata_manager):
    data = {"business": "A"}
    pdf_metadata_manager.create_metadata("/tmp/dup.pdf", data)
    with pytest.raises(ValueError):
        pdf_metadata_manager.create_metadata("/tmp/dup.pdf", data)

def test_create_metadata_empty_file(pdf_metadata_manager):
    with pytest.raises(ValueError):
        pdf_metadata_manager.create_metadata("", {"business": "A"})

def test_get_metadata_by_file_path(pdf_metadata_manager):
    data = {"business": "FindMe"}
    pdf_metadata_manager.create_metadata("/tmp/findme.pdf", data)
    metadata = pdf_metadata_manager.get_metadata_by_file_path("/tmp/findme.pdf")
    assert metadata is not None
    assert metadata["business"] == "FindMe"

def test_list_metadata(pdf_metadata_manager):
    pdf_metadata_manager.create_metadata("/tmp/a.pdf", {"business": "A"})
    pdf_metadata_manager.create_metadata("/tmp/b.pdf", {"business": "B"})
    all_metadata = pdf_metadata_manager.list_metadata()
    assert len(all_metadata) == 2
    file_paths = [m["file_path"] for m in all_metadata]
    assert "/tmp/a.pdf" in file_paths and "/tmp/b.pdf" in file_paths

def test_update_metadata(pdf_metadata_manager):
    data = {"business": "Old", "total": 1.0}
    mid = pdf_metadata_manager.create_metadata("/tmp/upd.pdf", data)
    pdf_metadata_manager.update_metadata(mid, {"business": "New", "total": 2.0})
    metadata = pdf_metadata_manager.get_metadata_by_id(mid)
    assert metadata["business"] == "New"
    assert metadata["total"] == 2.0

def test_update_metadata_no_fields(pdf_metadata_manager):
    data = {"business": "NoUpdate"}
    mid = pdf_metadata_manager.create_metadata("/tmp/noupd.pdf", data)
    with pytest.raises(ValueError):
        pdf_metadata_manager.update_metadata(mid, {})

def test_update_metadata_not_exist(pdf_metadata_manager):
    with pytest.raises(ValueError):
        pdf_metadata_manager.update_metadata(999, {"business": "X"})

def test_delete_metadata(pdf_metadata_manager):
    data = {"business": "ToDelete"}
    mid = pdf_metadata_manager.create_metadata("/tmp/del.pdf", data)
    pdf_metadata_manager.delete_metadata(mid)
    assert pdf_metadata_manager.get_metadata_by_id(mid) is None

def test_delete_metadata_not_exist(pdf_metadata_manager):
    with pytest.raises(ValueError):
        pdf_metadata_manager.delete_metadata(999) 

def test_get_business_by_name(db_manager):
    """Test getting a business by name."""
    # Add a business
    business_id = db_manager.add_business("TestCo")
    
    # Get business by name
    business = db_manager.get_business_by_name("TestCo")
    assert business is not None
    assert business["id"] == business_id
    assert business["name"] == "TestCo"
    
    # Test non-existent business
    business = db_manager.get_business_by_name("NonExistent")
    assert business is None

def test_get_business_by_name_case_sensitive(db_manager):
    """Test that get_business_by_name is case sensitive."""
    # Add a business with specific case
    business_id = db_manager.add_business("TestCo")
    
    # Get business with exact case
    business = db_manager.get_business_by_name("TestCo")
    assert business is not None
    assert business["id"] == business_id
    
    # Get business with different case
    business = db_manager.get_business_by_name("testco")
    assert business is None 

def test_update_business_name(db_manager):
    """Test updating a business name."""
    # Add a business
    business_id = db_manager.add_business("OldName")
    
    # Update the business name
    success = db_manager.update_business_name(business_id, "NewName")
    assert success is True
    
    # Verify the name was updated
    business = db_manager.get_business_by_name("NewName")
    assert business is not None
    assert business["id"] == business_id
    assert business["name"] == "NewName"
    
    # Verify old name no longer exists
    old_business = db_manager.get_business_by_name("OldName")
    assert old_business is None

def test_update_business_name_not_found(db_manager):
    """Test updating a business name that doesn't exist."""
    success = db_manager.update_business_name(999, "NewName")
    assert success is True  # SQLite UPDATE doesn't fail if no rows affected

def test_update_business_name_invalid_id(db_manager):
    """Test updating a business name with invalid ID."""
    success = db_manager.update_business_name(-1, "NewName")
    assert success is True  # SQLite UPDATE doesn't fail if no rows affected 
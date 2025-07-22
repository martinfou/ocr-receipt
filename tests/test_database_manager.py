import pytest
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.project_manager import ProjectManager

@pytest.fixture
def db_manager():
    db = DatabaseManager(":memory:")
    db.connect()
    db.execute_query("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)
    yield db
    db.close()

@pytest.fixture
def project_manager(db_manager):
    return ProjectManager(db_manager)

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
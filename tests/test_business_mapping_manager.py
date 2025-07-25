import pytest
from unittest.mock import MagicMock, ANY
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager

@pytest.fixture
def mock_db_manager():
    db = MagicMock()
    db.get_all_businesses.return_value = [
        {"id": 1, "name": "Acme Corp"},
        {"id": 2, "name": "Globex"}
    ]
    db.get_all_keywords.return_value = [
        {"business_name": "Acme Corp", "keyword": "Acme", "is_case_sensitive": 0},
        {"business_name": "Globex", "keyword": "Globex Inc", "is_case_sensitive": 0}
    ]
    db.add_business.return_value = 1
    db.add_keyword.return_value = True
    return db

@pytest.fixture
def manager(mock_db_manager):
    return BusinessMappingManager(mock_db_manager)

def test_add_business(manager, mock_db_manager):
    # Should not add duplicate
    assert not manager.add_business("Acme Corp")
    # Should add new
    mock_db_manager.get_all_businesses.return_value = []
    assert manager.add_business("NewCo")

def test_get_business_names(manager):
    names = manager.get_business_names()
    assert "Acme Corp" in names
    assert "Globex" in names

def test_add_keyword(manager, mock_db_manager):
    # Should add keyword for existing business
    assert manager.add_keyword("Acme Corp", "Acme")
    # Should not add keyword for non-existent business
    mock_db_manager.get_all_businesses.return_value = []
    assert not manager.add_keyword("NonExistent", "Foo")

def test_get_keywords(manager):
    keywords = manager.get_keywords()
    assert any(k["keyword"] == "Acme" for k in keywords)
    assert any(k["keyword"] == "Globex Inc" for k in keywords)

def test_find_business_match_exact(manager):
    # Exact match (case insensitive)
    result = manager.find_business_match("Acme")
    assert result == ("Acme Corp", "exact", 1.0)

def test_find_business_match_fuzzy(manager, mock_db_manager):
    # Fuzzy match (simulate FuzzyMatcher)
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Globex", "keyword": "Globex Inc", "is_case_sensitive": 0}
    ]
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: ("globex inc", 0.85) if text == "globex incorporated" else None
    result = manager.find_business_match("Globex Incorporated")
    assert result == ("Globex", "fuzzy", 0.85)

def test_find_business_match_none(manager, mock_db_manager):
    # No match
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: None
    result = manager.find_business_match("Unknown")
    assert result is None 

def test_find_business_match_exact_case_sensitive(manager, mock_db_manager):
    # Add a case-sensitive exact keyword
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Acme Corp", "keyword": "Acme", "is_case_sensitive": 1}
    ]
    # Should match only with exact case, else partial match with lower score
    assert manager.find_business_match("Acme") == ("Acme Corp", "exact", 1.0)
    assert manager.find_business_match("acme") == ("Acme Corp", "exact", 0.8)

def test_find_business_match_fuzzy_case_insensitive(manager, mock_db_manager):
    # Add a case-insensitive fuzzy keyword
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Globex", "keyword": "Globex Inc", "is_case_sensitive": 0}
    ]
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: ("globex inc", 0.85) if text == "globex incorporated" else None
    result = manager.find_business_match("Globex Incorporated")
    assert result == ("Globex", "fuzzy", 0.85)

def test_find_business_match_fuzzy_ocr_typo(manager, mock_db_manager):
    # Add a case-insensitive fuzzy keyword for OCR typo scenario
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Globex", "keyword": "Globex Inc", "is_case_sensitive": 0}
    ]
    # Mock the fuzzy matcher to return a match for the OCR typo
    def mock_find_best_match(query, candidates):
        if query == "globex lnc" and "globex inc" in candidates:
            return ("globex inc", 0.75)
        return None
    manager.fuzzy_matcher.find_best_match = mock_find_best_match
    result = manager.find_business_match("Globex lnc")
    assert result == ("Globex", "fuzzy", 0.75)

def test_find_business_match_fuzzy_case_sensitive_penalty(manager, mock_db_manager):
    # Add a case-sensitive fuzzy keyword
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Globex", "keyword": "Globex Inc", "is_case_sensitive": 1}
    ]
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: ("globex inc", 0.85) if text == "globex incorporated" else None
    result = manager.find_business_match("Globex Incorporated")
    assert result == ("Globex", "fuzzy", 0.68)  # 0.85 * 0.8 = 0.68

def test_add_business_adds_exact_keyword(manager, mock_db_manager):
    # Simulate adding a business
    business_list = []
    def get_all_businesses_side_effect():
        return business_list
    mock_db_manager.get_all_businesses.side_effect = get_all_businesses_side_effect
    mock_db_manager.add_business.side_effect = lambda name, meta: business_list.append({"id": 1, "name": name})        
    manager.add_business("TestBiz")
    mock_db_manager.add_keyword.assert_called_with(1, "TestBiz", 0) 
import pytest
from unittest.mock import MagicMock, ANY
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager

@pytest.fixture
def mock_db_manager():
    db = MagicMock()
    db.get_all_businesses.return_value = [
        {"id": 1, "business_name": "Acme Corp"},
        {"id": 2, "business_name": "Globex"}
    ]
    db.get_all_keywords.return_value = [
        {"business_name": "Acme Corp", "keyword": "Acme", "match_type": "exact"},
        {"business_name": "Acme Corp", "keyword": "Acme Corporation", "match_type": "variant"},
        {"business_name": "Globex", "keyword": "Globex Inc", "match_type": "exact"}
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
    assert manager.add_keyword("Acme Corp", "Acme", "exact")
    # Should not add keyword for non-existent business
    mock_db_manager.get_all_businesses.return_value = []
    assert not manager.add_keyword("NonExistent", "Foo", "exact")

def test_get_keywords(manager):
    keywords = manager.get_keywords()
    assert any(k["keyword"] == "Acme" for k in keywords)
    assert any(k["keyword"] == "Globex Inc" for k in keywords)

def test_find_business_match_exact(manager):
    # Exact match (case and punctuation sensitive)
    result = manager.find_business_match("Acme")
    assert result == ("Acme Corp", "exact", 1.0)

def test_find_business_match_variant(manager):
    # Variant match (normalize)
    result = manager.find_business_match("Acme Corporation")
    assert result == ("Acme Corp", "variant", 1.0)

def test_find_business_match_fuzzy(manager, mock_db_manager):
    # Fuzzy match (simulate FuzzyMatcher)
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Globex", "keyword": "Globex Inc", "match_type": "exact", "is_case_sensitive": 0}
    ]
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: ("globex inc", 0.85) if text == "globex incorporated" else None
    result = manager.find_business_match("Globex Incorporated")
    assert result == ("Globex", "fuzzy", 0.85)

def test_find_business_match_none(manager, mock_db_manager):
    # No match
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: None
    result = manager.find_business_match("Unknown")
    assert result is None 

def test_find_business_match_variant_100(manager, mock_db_manager):
    # Only a variant keyword for banque-td
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "banque-td", "keyword": "Toronto Dominion", "match_type": "variant"}
    ]
    result = manager.find_business_match("Toronto Dominion")
    assert result == ("banque-td", "variant", 1.0)

def test_find_business_match_exact_banque_td(manager, mock_db_manager):
    # Only an exact keyword for banque-td
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "banque-td", "keyword": "banque-td", "match_type": "exact"}
    ]
    result = manager.find_business_match("banque-td")
    assert result == ("banque-td", "exact", 1.0) 

def test_find_business_match_exact_case_sensitive(manager, mock_db_manager):
    # Add a case-sensitive exact keyword
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Acme Corp", "keyword": "Acme", "match_type": "exact", "is_case_sensitive": 1}
    ]
    # Should match only with exact case, else partial match with lower score
    assert manager.find_business_match("Acme") == ("Acme Corp", "exact", 1.0)
    assert manager.find_business_match("acme") == ("Acme Corp", "exact", 0.8)

def test_find_business_match_variant_case_sensitive(manager, mock_db_manager):
    # Add a case-sensitive variant keyword
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Acme Corp", "keyword": "Acme Corporation", "match_type": "variant", "is_case_sensitive": 1}
    ]
    # Should match only with exact case after normalization, else partial match with lower score
    assert manager.find_business_match("Acme Corporation") == ("Acme Corp", "variant", 1.0)
    assert manager.find_business_match("acme corporation") == ("Acme Corp", "variant", 0.8)

def test_find_business_match_fuzzy_case_insensitive(manager, mock_db_manager):
    # Add a case-insensitive fuzzy keyword
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Acme Corp", "keyword": "Acme", "match_type": "exact", "is_case_sensitive": 0}
    ]
    # Should match exact if lowercased matches, else fuzzy
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: (candidates[0], 0.8)
    assert manager.find_business_match("acme") == ("Acme Corp", "exact", 1.0)
    # Use a text that is not a substring of the keyword to trigger fuzzy
    assert manager.find_business_match("acmex") == ("Acme Corp", "fuzzy", 0.8)

def test_find_business_match_fuzzy_ocr_typo(manager, mock_db_manager):
    # Add a case-insensitive fuzzy keyword for OCR typo scenario
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "banque-td", "keyword": "Toronto Dominion", "match_type": "variant", "is_case_sensitive": 0}
    ]
    # Simulate fuzzy matcher returning a match for OCR typo
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: ("toronto dominion", 0.85) if text == "torento dominian" else None
    assert manager.find_business_match("Torento Dominian") == ("banque-td", "fuzzy", 0.85)

def test_find_business_match_fuzzy_case_sensitive_penalty(manager, mock_db_manager):
    # Add a case-sensitive fuzzy keyword
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Acme Corp", "keyword": "Acme", "match_type": "exact", "is_case_sensitive": 1}
    ]
    # Should return exact with lower score for partial case-insensitive match
    assert manager.find_business_match("acme") == ("Acme Corp", "exact", 0.8)
    # Now test penalized fuzzy: input is 'acmex', mock returns ('acme', 0.9)
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: ("acme", 0.9) if text == "acmex" else None
    assert manager.find_business_match("acmex") == ("Acme Corp", "fuzzy", 0.9 * 0.8)
    # Should return full confidence for case-sensitive fuzzy match
    manager.fuzzy_matcher.find_best_match = lambda text, candidates: ("Acme", 0.9) if text == "Acme" else None
    assert manager.find_business_match("Acme") == ("Acme Corp", "exact", 1.0)

def test_add_business_adds_exact_keyword(manager, mock_db_manager):
    # Simulate adding a business
    business_list = []
    def get_all_businesses_side_effect():
        return business_list
    mock_db_manager.get_all_businesses.side_effect = get_all_businesses_side_effect
    mock_db_manager.add_business.side_effect = lambda name, meta: business_list.append({"id": 1, "business_name": name})
    manager.add_business("TestBiz")
    mock_db_manager.add_keyword.assert_called_with(1, "TestBiz", "exact", 0)

def test_find_business_match_exact_case_sensitive_partial(manager, mock_db_manager):
    # Add a case-sensitive exact keyword
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Acme Corp", "keyword": "Acme", "match_type": "exact", "is_case_sensitive": 1}
    ]
    # Should match with lower score if only case-insensitive
    assert manager.find_business_match("acme") == ("Acme Corp", "exact", 0.8)

def test_find_business_match_variant_case_sensitive_partial(manager, mock_db_manager):
    # Add a case-sensitive variant keyword
    mock_db_manager.get_all_keywords.return_value = [
        {"business_name": "Acme Corp", "keyword": "Acme Corporation", "match_type": "variant", "is_case_sensitive": 1}
    ]
    # Should match with lower score if only case-insensitive after normalization
    assert manager.find_business_match("acme corporation") == ("Acme Corp", "variant", 0.8) 
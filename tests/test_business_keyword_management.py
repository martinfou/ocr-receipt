import pytest
from unittest.mock import Mock, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.gui.business_keywords_tab import BusinessKeywordsTab
from ocr_receipt.gui.dialogs.add_keyword_dialog import AddKeywordDialog

@pytest.fixture
def app():
    """Create a QApplication instance for testing."""
    return QApplication([])

@pytest.fixture
def mock_db_manager():
    """Create a mock database manager."""
    db_manager = Mock(spec=DatabaseManager)
    
    # Mock business data
    businesses = [
        {"id": 1, "name": "Test Business 1"},
        {"id": 2, "name": "Test Business 2"}
    ]
    
    # Mock keyword data
    keywords = [
        {
            "keyword": "test1",
            "is_case_sensitive": 0,
            "match_type": "exact",
            "last_used": None,
            "usage_count": 0,
            "business_name": "Test Business 1"
        },
        {
            "keyword": "test2",
            "is_case_sensitive": 1,
            "match_type": "fuzzy",
            "last_used": None,
            "usage_count": 0,
            "business_name": "Test Business 1"
        },
        {
            "keyword": "test3",
            "is_case_sensitive": 0,
            "match_type": "exact",
            "last_used": None,
            "usage_count": 0,
            "business_name": "Test Business 2"
        }
    ]
    
    db_manager.get_all_businesses.return_value = businesses
    db_manager.get_all_keywords.return_value = keywords
    db_manager.get_business_by_name.side_effect = lambda name: next((b for b in businesses if b["name"] == name), None)
    db_manager.add_keyword.return_value = True
    db_manager.delete_keyword.return_value = True
    db_manager.execute_query.return_value = Mock()
    
    return db_manager

@pytest.fixture
def business_mapping_manager(mock_db_manager):
    """Create a business mapping manager with mock database."""
    return BusinessMappingManager(mock_db_manager)

@pytest.fixture
def business_keywords_tab(business_mapping_manager, app):
    """Create a business keywords tab for testing."""
    return BusinessKeywordsTab(business_mapping_manager)

class TestBusinessKeywordManagement:
    """Test the enhanced business keyword management functionality."""
    
    def test_get_keywords_for_business(self, business_mapping_manager):
        """Test getting keywords for a specific business."""
        keywords = business_mapping_manager.get_keywords_for_business("Test Business 1")
        assert len(keywords) == 2
        assert all(kw["business_name"] == "Test Business 1" for kw in keywords)
        
        keywords = business_mapping_manager.get_keywords_for_business("Test Business 2")
        assert len(keywords) == 1
        assert keywords[0]["business_name"] == "Test Business 2"
        
        keywords = business_mapping_manager.get_keywords_for_business("Non-existent Business")
        assert len(keywords) == 0
    
    def test_get_keyword_count_for_business(self, business_mapping_manager):
        """Test getting keyword count for a specific business."""
        count = business_mapping_manager.get_keyword_count_for_business("Test Business 1")
        assert count == 2
        
        count = business_mapping_manager.get_keyword_count_for_business("Test Business 2")
        assert count == 1
        
        count = business_mapping_manager.get_keyword_count_for_business("Non-existent Business")
        assert count == 0
    
    def test_is_last_keyword_for_business(self, business_mapping_manager):
        """Test checking if a keyword is the last for a business."""
        # Test Business 1 has 2 keywords, so neither is the last
        assert not business_mapping_manager.is_last_keyword_for_business("Test Business 1", "test1")
        assert not business_mapping_manager.is_last_keyword_for_business("Test Business 1", "test2")
        
        # Test Business 2 has 1 keyword, so it is the last
        assert business_mapping_manager.is_last_keyword_for_business("Test Business 2", "test3")
        
        # Non-existent keyword should return False
        assert not business_mapping_manager.is_last_keyword_for_business("Test Business 1", "non-existent")
    
    def test_add_keyword_dialog_creation(self, app):
        """Test creating the add keyword dialog."""
        business_names = ["Business 1", "Business 2", "Business 3"]
        dialog = AddKeywordDialog(business_names)
        
        assert dialog.business_combo.count() == 4  # 1 placeholder + 3 businesses
        assert dialog.business_combo.itemText(0) == "Select a business..."
        assert dialog.business_combo.itemText(1) == "Business 1"
        assert dialog.business_combo.itemText(2) == "Business 2"
        assert dialog.business_combo.itemText(3) == "Business 3"
        
        dialog.close()
    
    def test_add_keyword_dialog_validation(self, app):
        """Test add keyword dialog validation."""
        business_names = ["Test Business"]
        dialog = AddKeywordDialog(business_names)
        
        # Initially, OK button should be disabled
        assert not dialog.ok_button.isEnabled()
        
        # Select business but no keyword
        dialog.business_combo.setCurrentIndex(1)
        assert not dialog.ok_button.isEnabled()
        
        # Add keyword
        dialog.keyword_edit.setText("test keyword")
        assert dialog.ok_button.isEnabled()
        
        # Clear keyword
        dialog.keyword_edit.clear()
        assert not dialog.ok_button.isEnabled()
        
        dialog.close()
    
    def test_add_keyword_dialog_accept(self, app):
        """Test add keyword dialog accept functionality."""
        business_names = ["Test Business"]
        dialog = AddKeywordDialog(business_names)
        
        # Set up dialog
        dialog.business_combo.setCurrentIndex(1)
        dialog.keyword_edit.setText("test keyword")
        dialog.case_sensitive_checkbox.setChecked(True)
        dialog.match_type_combo.setCurrentIndex(1)  # Fuzzy match
        
        # Simulate accept
        dialog._on_accept()
        
        assert dialog.get_business_name() == "Test Business"
        assert dialog.get_keyword() == "test keyword"
        assert dialog.get_is_case_sensitive() is True
        assert dialog.get_match_type() == "fuzzy"
        
        dialog.close()
    
    def test_business_keywords_tab_has_new_buttons(self, business_keywords_tab):
        """Test that the business keywords tab has the new buttons."""
        assert hasattr(business_keywords_tab, 'add_keyword_button')
        assert hasattr(business_keywords_tab, 'delete_business_button')
        assert business_keywords_tab.add_keyword_button is not None
        assert business_keywords_tab.delete_business_button is not None
    
    def test_add_keyword_handler_no_businesses(self, business_keywords_tab, monkeypatch):
        """Test add keyword handler when no businesses exist."""
        # Mock get_business_names to return empty list
        monkeypatch.setattr(business_keywords_tab.business_mapping_manager, 'get_business_names', lambda: [])
        
        # Mock QMessageBox.information
        mock_message_box = Mock()
        monkeypatch.setattr('ocr_receipt.gui.business_keywords_tab.QMessageBox.information', mock_message_box)
        
        business_keywords_tab._on_add_keyword()
        
        mock_message_box.assert_called_once()
    
    def test_add_keyword_handler_with_businesses(self, business_keywords_tab, monkeypatch):
        """Test add keyword handler when businesses exist."""
        # Mock get_business_names to return business list
        monkeypatch.setattr(business_keywords_tab.business_mapping_manager, 'get_business_names', 
                           lambda: ["Test Business 1", "Test Business 2"])
        
        # Mock AddKeywordDialog
        mock_dialog = Mock()
        mock_dialog.exec.return_value = 1  # Accepted
        mock_dialog.get_business_name.return_value = "Test Business 1"
        mock_dialog.get_keyword.return_value = "new keyword"
        mock_dialog.get_is_case_sensitive.return_value = False
        mock_dialog.get_match_type.return_value = "exact"
        
        monkeypatch.setattr('ocr_receipt.gui.business_keywords_tab.AddKeywordDialog', 
                           lambda business_names, parent: mock_dialog)
        
        # Mock add_keyword to return success
        mock_add_keyword = Mock(return_value=True)
        monkeypatch.setattr(business_keywords_tab.business_mapping_manager, 'add_keyword', mock_add_keyword)
        
        # Mock QMessageBox.information for success
        mock_message_box = Mock()
        monkeypatch.setattr('ocr_receipt.gui.business_keywords_tab.QMessageBox.information', mock_message_box)
        
        business_keywords_tab._on_add_keyword()
        
        # Verify dialog was created and add_keyword was called
        mock_dialog.exec.assert_called_once()
        mock_add_keyword.assert_called_once_with(
            "Test Business 1", "new keyword", is_case_sensitive=0, match_type="exact"
        )
        mock_message_box.assert_called_once() 
    
    def test_delete_last_keyword_deletes_business(self, business_keywords_tab, monkeypatch):
        """Test that deleting the last keyword for a business also deletes the business."""
        # Mock get_selected_keywords to return a keyword that is the last for its business
        selected_keywords = [{'business_name': 'Test Business', 'keyword': 'test keyword'}]
        monkeypatch.setattr(business_keywords_tab.keywords_table, 'get_selected_keywords', 
                           lambda: selected_keywords)
        
        # Mock is_last_keyword_for_business to return True
        monkeypatch.setattr(business_keywords_tab.business_mapping_manager, 'is_last_keyword_for_business', 
                           lambda business_name, keyword: True)
        
        # Mock QMessageBox.question to return Yes for both confirmations
        from PyQt6.QtWidgets import QMessageBox
        mock_question = Mock()
        mock_question.side_effect = [QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.Yes]  # Yes for both confirmations
        monkeypatch.setattr('ocr_receipt.gui.business_keywords_tab.QMessageBox.question', mock_question)
        
        # Mock delete_keyword to return success
        mock_delete_keyword = Mock(return_value=True)
        monkeypatch.setattr(business_keywords_tab.business_mapping_manager, 'delete_keyword', mock_delete_keyword)
        
        # Mock delete_business
        mock_delete_business = Mock(return_value=True)
        monkeypatch.setattr(business_keywords_tab.business_mapping_manager, 'delete_business', mock_delete_business)
        
        # Mock QMessageBox.information for success message
        mock_information = Mock()
        monkeypatch.setattr('ocr_receipt.gui.business_keywords_tab.QMessageBox.information', mock_information)
        
        # Call the method
        business_keywords_tab._on_delete_keyword()
        
        # Verify that both delete_keyword and delete_business were called
        mock_delete_keyword.assert_called_once_with('Test Business', 'test keyword')
        mock_delete_business.assert_called_once_with('Test Business')
        
        # Verify that the confirmation dialogs were shown
        assert mock_question.call_count == 2 
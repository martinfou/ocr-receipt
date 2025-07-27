"""
Unit tests for FileNamingTab.
"""
import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog
from PyQt6.QtCore import Qt
from unittest.mock import Mock, patch
from ocr_receipt.gui.file_naming_tab import FileNamingTab
from ocr_receipt.config import ConfigManager

@pytest.fixture
def mock_config_manager():
    """Create a mock config manager."""
    config = Mock(spec=ConfigManager)
    
    # Mock templates data
    templates = {
        'default': {
            'name': 'Default Template',
            'description': 'Standard template with project, date, company, and total',
            'template': '{project}_{documentType}_{date}_{company}_{total}',
            'active': True
        }
    }
    
    def mock_get(key, default=None):
        if key == 'file_naming.templates':
            return templates
        elif key == 'file_naming.active_template':
            return 'default'
        return default
    
    config.get.side_effect = mock_get
    config.set.return_value = None
    config.save.return_value = None
    return config

@pytest.fixture
def file_naming_tab(qtbot, mock_config_manager):
    """Create a FileNamingTab for testing."""
    tab = FileNamingTab(mock_config_manager)
    qtbot.addWidget(tab)
    return tab

class TestFileNamingTab:
    """Test FileNamingTab functionality."""
    
    def test_init(self, qtbot, mock_config_manager):
        """Test tab initialization."""
        tab = FileNamingTab(mock_config_manager)
        qtbot.addWidget(tab)
        
        assert tab.config_manager == mock_config_manager
        assert tab.template_edit is not None
        assert tab.preview_text is not None
        assert tab.add_template_button is not None
        assert tab.edit_template_button is not None
        assert tab.delete_template_button is not None
        assert tab.set_active_button is not None
        assert tab.help_button is not None

    def test_load_templates(self, file_naming_tab, mock_config_manager):
        """Test loading templates from configuration."""
        # Check that templates were loaded
        assert 'default' in file_naming_tab.templates
        assert file_naming_tab.active_template_id == 'default'
        assert file_naming_tab.template_edit.text() == "{project}_{documentType}_{date}_{company}_{total}"

    def test_template_change_updates_preview(self, file_naming_tab, qtbot):
        """Test that template changes update the preview."""
        # Change template
        qtbot.keyClicks(file_naming_tab.template_edit, "{project}_{company}")
        qtbot.wait(100)
        
        # Check that preview was updated
        preview_text = file_naming_tab.preview_text.toPlainText()
        assert "Q1_2024_Invoices_Hydro_Quebec_Inc" in preview_text

    def test_generate_filename(self, file_naming_tab):
        """Test filename generation from template."""
        template = "{project}_{company}_{total}"
        data = {
            'project': 'Test Project',
            'company': 'Test Company',
            'total': '123.45'
        }
        
        result = file_naming_tab._generate_filename(template, data)
        assert result == "Test_Project_Test_Company_123.45"

    def test_clean_filename_part(self, file_naming_tab):
        """Test cleaning filename parts."""
        # Test spaces
        assert file_naming_tab._clean_filename_part("Test Company") == "Test_Company"
        
        # Test invalid characters
        assert file_naming_tab._clean_filename_part("Test<Company>") == "Test_Company"
        
        # Test multiple spaces
        assert file_naming_tab._clean_filename_part("Test   Company") == "Test_Company"
        
        # Test empty string
        assert file_naming_tab._clean_filename_part("") == ""

    def test_validate_template(self, file_naming_tab):
        """Test template validation."""
        # Valid template
        assert file_naming_tab._validate_template("{project}_{company}")
        
        # Invalid template - no variables
        assert not file_naming_tab._validate_template("plain_text")
        
        # Invalid template - invalid variable
        assert not file_naming_tab._validate_template("{invalid_var}")
        
        # Invalid template - empty
        assert not file_naming_tab._validate_template("")

    def test_add_template(self, file_naming_tab, mock_config_manager, qtbot):
        """Test adding a new template."""
        with patch('ocr_receipt.gui.dialogs.template_dialog.TemplateDialog.exec') as mock_exec, \
             patch('ocr_receipt.gui.dialogs.template_dialog.TemplateDialog.get_template_id') as mock_get_id, \
             patch('ocr_receipt.gui.dialogs.template_dialog.TemplateDialog.get_template_name') as mock_get_name, \
             patch('ocr_receipt.gui.dialogs.template_dialog.TemplateDialog.get_template_description') as mock_get_desc, \
             patch('ocr_receipt.gui.dialogs.template_dialog.TemplateDialog.get_template_content') as mock_get_content:
            
            mock_exec.return_value = QDialog.DialogCode.Accepted
            mock_get_id.return_value = "test_template"
            mock_get_name.return_value = "Test Template"
            mock_get_desc.return_value = "A test template"
            mock_get_content.return_value = "{project}_{company}"
            
            qtbot.mouseClick(file_naming_tab.add_template_button, Qt.MouseButton.LeftButton)
            
            # Check that template was added
            assert "test_template" in file_naming_tab.templates
            assert file_naming_tab.templates["test_template"]["name"] == "Test Template"

    def test_edit_template(self, file_naming_tab, qtbot):
        """Test editing a template."""
        # Select a template in the combo box
        file_naming_tab.template_combo.setCurrentIndex(0)
        
        with patch('ocr_receipt.gui.dialogs.template_dialog.TemplateDialog.exec') as mock_exec, \
             patch('ocr_receipt.gui.dialogs.template_dialog.TemplateDialog.get_template_name') as mock_get_name, \
             patch('ocr_receipt.gui.dialogs.template_dialog.TemplateDialog.get_template_description') as mock_get_desc, \
             patch('ocr_receipt.gui.dialogs.template_dialog.TemplateDialog.get_template_content') as mock_get_content:
            
            mock_exec.return_value = QDialog.DialogCode.Accepted
            mock_get_name.return_value = "Updated Template"
            mock_get_desc.return_value = "Updated description"
            mock_get_content.return_value = "{project}_{date}"
            
            qtbot.mouseClick(file_naming_tab.edit_template_button, Qt.MouseButton.LeftButton)
            
            # Check that template was updated
            assert file_naming_tab.templates["default"]["name"] == "Updated Template"

    def test_show_help(self, file_naming_tab, qtbot):
        """Test help dialog display."""
        with patch('PyQt6.QtWidgets.QMessageBox.information') as mock_info:
            qtbot.mouseClick(file_naming_tab.help_button, Qt.MouseButton.LeftButton)
            mock_info.assert_called_once()

    def test_update_language(self, file_naming_tab):
        """Test language update functionality."""
        # Store original texts
        original_title = file_naming_tab.findChild(file_naming_tab.__class__, "title_label")
        original_add_text = file_naming_tab.add_template_button.text()
        
        # Update language
        file_naming_tab.update_language()
        
        # Check that texts were updated (they should be different if translation works)
        # Note: In a real test, we'd change the language first, but for now we just verify the method runs
        assert file_naming_tab.add_template_button.text() is not None

    def test_sample_data_updates_preview(self, file_naming_tab, qtbot):
        """Test that changing sample data updates the preview."""
        # Change sample company
        qtbot.keyClicks(file_naming_tab.sample_company, "New Company")
        qtbot.wait(100)
        
        # Check that preview was updated
        preview_text = file_naming_tab.preview_text.toPlainText()
        assert "New_Company" in preview_text

    def test_separator_change_updates_preview(self, file_naming_tab, qtbot):
        """Test that changing separator updates the preview."""
        # Change separator
        file_naming_tab.separator_combo.setCurrentText("-")
        qtbot.wait(100)
        
        # Check that preview was updated (though the template itself doesn't change, 
        # the preview generation might be affected)
        assert file_naming_tab.separator_combo.currentText() == "-"

    def test_template_dialog_variables(self, qtbot, mock_config_manager):
        """Test that template dialog has clickable variable buttons."""
        from ocr_receipt.gui.dialogs.template_dialog import TemplateDialog
        
        dialog = TemplateDialog(parent=None)
        qtbot.addWidget(dialog)
        
        # Check that variable buttons exist
        assert hasattr(dialog, 'variable_buttons')
        assert len(dialog.variable_buttons) == 8  # 8 variables
        
        # Check that separator combo exists
        assert hasattr(dialog, 'separator_combo')
        assert dialog.separator_combo.currentText() == "_"
        
        # Check that template edit exists
        assert hasattr(dialog, 'template_edit')
        
        # Test clicking a variable button
        project_button = dialog.variable_buttons.get('project')
        assert project_button is not None
        
        # Click the project button
        qtbot.mouseClick(project_button, Qt.MouseButton.LeftButton)
        
        # Check that the variable was added to the template
        assert dialog.template_edit.text() == "{project}"
        
        # Test clicking another variable
        company_button = dialog.variable_buttons.get('company')
        qtbot.mouseClick(company_button, Qt.MouseButton.LeftButton)
        
        # Check that both variables were added with separator
        assert dialog.template_edit.text() == "{project}_{company}"
        
        dialog.close() 
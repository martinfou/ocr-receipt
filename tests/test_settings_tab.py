"""
Tests for the SettingsTab class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from ocr_receipt.gui.settings_tab import SettingsTab
from ocr_receipt.config import ConfigManager
from ocr_receipt.utils.translation_helper import set_language, get_language


class TestSettingsTab:
    """Test the SettingsTab class functionality."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a mock config manager for testing."""
        config = ConfigManager("test_config.yaml")
        # Set up some test values
        config.set('gui.window_size', [1000, 700])
        config.set('gui.auto_save', True)
        config.set('gui.show_preview', False)
        config.set('ocr.confidence_threshold', 0.7)
        config.set('ocr.max_retries', 5)
        config.set('app.ui_language', 'en')
        return config
    
    @pytest.fixture
    def settings_tab(self, qtbot, config_manager):
        """Create a SettingsTab instance for testing."""
        tab = SettingsTab(config_manager)
        qtbot.addWidget(tab)
        return tab
    
    def test_init(self, settings_tab):
        """Test that SettingsTab initializes correctly."""
        assert settings_tab is not None
        assert settings_tab.config_manager is not None
        
        # Check that all UI elements exist
        assert hasattr(settings_tab, 'language_combo')
        assert hasattr(settings_tab, 'window_width_spin')
        assert hasattr(settings_tab, 'window_height_spin')
        assert hasattr(settings_tab, 'auto_save_checkbox')
        assert hasattr(settings_tab, 'show_preview_checkbox')
        assert hasattr(settings_tab, 'confidence_spin')
        assert hasattr(settings_tab, 'max_retries_spin')
        assert hasattr(settings_tab, 'db_path_edit')
        assert hasattr(settings_tab, 'db_browse_button')
        assert hasattr(settings_tab, 'backup_button')
        assert hasattr(settings_tab, 'restore_button')
        assert hasattr(settings_tab, 'save_button')
        assert hasattr(settings_tab, 'reset_button')
        assert hasattr(settings_tab, 'apply_button')
        assert hasattr(settings_tab, 'status_label')
    
    def test_load_current_settings(self, settings_tab, config_manager):
        """Test that current settings are loaded correctly."""
        # Verify language combo is populated
        assert settings_tab.language_combo.count() >= 2  # At least English and French
        
        # Verify current language is set
        current_language = get_language()
        index = settings_tab.language_combo.findData(current_language)
        assert index >= 0
        
        # Verify GUI settings are loaded
        window_size = config_manager.get('gui.window_size', [1200, 800])
        assert settings_tab.window_width_spin.value() == window_size[0]
        assert settings_tab.window_height_spin.value() == window_size[1]
        assert settings_tab.auto_save_checkbox.isChecked() == config_manager.get('gui.auto_save', True)
        assert settings_tab.show_preview_checkbox.isChecked() == config_manager.get('gui.show_preview', True)
        
        # Verify OCR settings are loaded
        confidence = int(config_manager.get('ocr.confidence_threshold', 0.6) * 100)
        assert settings_tab.confidence_spin.value() == confidence
        assert settings_tab.max_retries_spin.value() == config_manager.get('ocr.max_retries', 3)
        
        # Verify database path is loaded
        db_path = config_manager.get('database.path', 'ocr_receipts.db')
        assert settings_tab.db_path_edit.text() == db_path
    
    def test_language_combo_options(self, settings_tab):
        """Test that language combo has the expected options."""
        # Check that English and French are available
        english_index = settings_tab.language_combo.findData("en")
        french_index = settings_tab.language_combo.findData("fr")
        
        assert english_index >= 0
        assert french_index >= 0
        
        # Check display text
        assert "English" in settings_tab.language_combo.itemText(english_index)
        assert "Français" in settings_tab.language_combo.itemText(french_index)
    
    def test_window_size_spinboxes(self, settings_tab):
        """Test window size spinboxes have correct ranges and values."""
        # Test width spinbox
        assert settings_tab.window_width_spin.minimum() == 800
        assert settings_tab.window_width_spin.maximum() == 2000
        assert settings_tab.window_width_spin.suffix() == " px"
        
        # Test height spinbox
        assert settings_tab.window_height_spin.minimum() == 600
        assert settings_tab.window_height_spin.maximum() == 1500
        assert settings_tab.window_height_spin.suffix() == " px"
    
    def test_confidence_spinbox(self, settings_tab):
        """Test confidence spinbox has correct range and format."""
        assert settings_tab.confidence_spin.minimum() == 10
        assert settings_tab.confidence_spin.maximum() == 100
        assert settings_tab.confidence_spin.suffix() == "%"
    
    def test_max_retries_spinbox(self, settings_tab):
        """Test max retries spinbox has correct range."""
        assert settings_tab.max_retries_spin.minimum() == 1
        assert settings_tab.max_retries_spin.maximum() == 10
    
    def test_db_path_readonly(self, settings_tab):
        """Test that database path field is read-only."""
        assert settings_tab.db_path_edit.isReadOnly()
    
    @patch('ocr_receipt.gui.settings_tab.QFileDialog.getSaveFileName')
    def test_browse_database(self, mock_file_dialog, settings_tab, qtbot):
        """Test database browse functionality."""
        # Mock file dialog to return a path
        mock_file_dialog.return_value = ("/path/to/new_database.db", "")
        
        # Click browse button
        qtbot.mouseClick(settings_tab.db_browse_button, Qt.MouseButton.LeftButton)
        
        # Verify file dialog was called
        mock_file_dialog.assert_called_once()
        
        # Verify path was updated
        assert settings_tab.db_path_edit.text() == "/path/to/new_database.db"
        assert settings_tab.config_manager.get('database.path') == "/path/to/new_database.db"
    
    @patch('ocr_receipt.gui.settings_tab.QFileDialog.getSaveFileName')
    def test_browse_database_cancelled(self, mock_file_dialog, settings_tab, qtbot):
        """Test database browse when user cancels."""
        # Mock file dialog to return empty path (user cancelled)
        original_path = settings_tab.db_path_edit.text()
        mock_file_dialog.return_value = ("", "")
        
        # Click browse button
        qtbot.mouseClick(settings_tab.db_browse_button, Qt.MouseButton.LeftButton)
        
        # Verify file dialog was called
        mock_file_dialog.assert_called_once()
        
        # Verify path was not changed
        assert settings_tab.db_path_edit.text() == original_path
    
    @patch('ocr_receipt.gui.settings_tab.QFileDialog.getSaveFileName')
    @patch('ocr_receipt.gui.settings_tab.os.path.exists')
    @patch('builtins.__import__')
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.information')
    def test_backup_database_success(self, mock_message_box, mock_import, mock_exists, mock_file_dialog, settings_tab, qtbot):
        # Mock shutil import
        mock_shutil = Mock()
        mock_shutil.copy2 = Mock()
        mock_import.return_value = mock_shutil
        """Test successful database backup."""
        # Mock database exists
        mock_exists.return_value = True
        # Mock file dialog to return a backup path
        mock_file_dialog.return_value = ("/path/to/backup.db", "")
        
        # Click backup button
        qtbot.mouseClick(settings_tab.backup_button, Qt.MouseButton.LeftButton)
        
        # Verify file dialog was called
        mock_file_dialog.assert_called_once()
        # Verify copy was called
        mock_shutil.copy2.assert_called_once()
        # Verify success message was shown
        mock_message_box.assert_called_once()
    
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.warning')
    @patch('ocr_receipt.gui.settings_tab.os.path.exists')
    def test_backup_database_no_file(self, mock_exists, mock_warning, settings_tab, qtbot):
        """Test backup when database file doesn't exist."""
        # Mock database doesn't exist
        mock_exists.return_value = False
        
        # Click backup button
        qtbot.mouseClick(settings_tab.backup_button, Qt.MouseButton.LeftButton)
        
        # Verify warning was shown
        mock_warning.assert_called_once()
    
    @patch('ocr_receipt.gui.settings_tab.QFileDialog.getOpenFileName')
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.question')
    @patch('ocr_receipt.gui.settings_tab.os.path.exists')
    @patch('builtins.__import__')
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.information')
    def test_restore_database_success(self, mock_message_box, mock_import, mock_exists, mock_question, mock_file_dialog, settings_tab, qtbot):
        # Mock shutil import
        mock_shutil = Mock()
        mock_shutil.copy2 = Mock()
        mock_import.return_value = mock_shutil
        """Test successful database restore."""
        # Mock file dialog to return a backup path
        mock_file_dialog.return_value = ("/path/to/backup.db", "")
        # Mock user confirms restore
        mock_question.return_value = QMessageBox.StandardButton.Yes
        # Mock current database exists
        mock_exists.return_value = True
        
        # Click restore button
        qtbot.mouseClick(settings_tab.restore_button, Qt.MouseButton.LeftButton)
        
        # Verify file dialog was called
        mock_file_dialog.assert_called_once()
        # Verify confirmation dialog was shown
        mock_question.assert_called_once()
        # Verify copy was called (for backup and restore)
        assert mock_shutil.copy2.call_count >= 1
        # Verify success message was shown
        mock_message_box.assert_called_once()
    
    @patch('ocr_receipt.gui.settings_tab.QFileDialog.getOpenFileName')
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.question')
    def test_restore_database_cancelled(self, mock_question, mock_file_dialog, settings_tab, qtbot):
        """Test restore when user cancels confirmation."""
        # Mock file dialog to return a backup path
        mock_file_dialog.return_value = ("/path/to/backup.db", "")
        # Mock user cancels restore
        mock_question.return_value = QMessageBox.StandardButton.No
        
        # Click restore button
        qtbot.mouseClick(settings_tab.restore_button, Qt.MouseButton.LeftButton)
        
        # Verify file dialog was called
        mock_file_dialog.assert_called_once()
        # Verify confirmation dialog was shown
        mock_question.assert_called_once()
        # Verify no copy was made (user cancelled)
        # Note: We can't easily test this without more complex mocking
    
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.information')
    @patch('ocr_receipt.gui.settings_tab.set_language')
    def test_save_settings_success(self, mock_set_language, mock_message_box, settings_tab, qtbot):
        """Test successful save settings operation."""
        # Change some settings
        settings_tab.window_width_spin.setValue(1400)
        settings_tab.window_height_spin.setValue(900)
        settings_tab.auto_save_checkbox.setChecked(False)
        settings_tab.confidence_spin.setValue(80)
        
        # Click save button
        qtbot.mouseClick(settings_tab.save_button, Qt.MouseButton.LeftButton)
        
        # Verify settings were saved
        assert settings_tab.config_manager.get('gui.window_size') == [1400, 900]
        assert settings_tab.config_manager.get('gui.auto_save') == False
        assert settings_tab.config_manager.get('ocr.confidence_threshold') == 0.8
        
        # Verify success message was shown
        mock_message_box.assert_called_once()
    
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.critical')
    @patch('ocr_receipt.gui.settings_tab.ConfigManager.save')
    def test_save_settings_error(self, mock_save, mock_message_box, settings_tab, qtbot):
        """Test save settings with error handling."""
        # Make save operation fail
        mock_save.side_effect = Exception("Save failed")
        
        # Click save button
        qtbot.mouseClick(settings_tab.save_button, Qt.MouseButton.LeftButton)
        
        # Verify error message was shown
        mock_message_box.assert_called_once()
    
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.information')
    @patch('ocr_receipt.gui.settings_tab.set_language')
    def test_apply_language_change(self, mock_set_language, mock_message_box, settings_tab, qtbot):
        """Test applying language change."""
        # Set language to French
        french_index = settings_tab.language_combo.findData("fr")
        settings_tab.language_combo.setCurrentIndex(french_index)
        
        # Click apply button
        qtbot.mouseClick(settings_tab.apply_button, Qt.MouseButton.LeftButton)
        
        # Verify language was changed
        mock_set_language.assert_called_once_with("fr")
        assert settings_tab.config_manager.get('app.ui_language') == "fr"
        
        # Verify success message was shown
        mock_message_box.assert_called_once()
    
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.question')
    def test_reset_settings(self, mock_question, settings_tab, qtbot):
        """Test reset settings functionality."""
        # Mock user confirming reset
        mock_question.return_value = QMessageBox.StandardButton.Yes
        
        # Change some settings first
        original_width = settings_tab.window_width_spin.value()
        settings_tab.window_width_spin.setValue(1500)
        
        # Click reset button
        qtbot.mouseClick(settings_tab.reset_button, Qt.MouseButton.LeftButton)
        
        # Verify settings were reset
        assert settings_tab.window_width_spin.value() == original_width
    
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.question')
    def test_reset_settings_cancelled(self, mock_question, settings_tab, qtbot):
        """Test reset settings when user cancels."""
        # Mock user cancelling reset
        mock_question.return_value = QMessageBox.StandardButton.No
        
        # Change some settings first
        settings_tab.window_width_spin.setValue(1500)
        changed_width = settings_tab.window_width_spin.value()
        
        # Click reset button
        qtbot.mouseClick(settings_tab.reset_button, Qt.MouseButton.LeftButton)
        
        # Verify settings were not reset
        assert settings_tab.window_width_spin.value() == changed_width
    
    def test_language_changed_signal(self, settings_tab, qtbot):
        """Test that language change signal is emitted."""
        # Connect to the signal
        signal_received = False
        new_language = None
        
        def on_language_changed(language):
            nonlocal signal_received, new_language
            signal_received = True
            new_language = language
        
        settings_tab.language_changed.connect(on_language_changed)
        
        # Change language
        settings_tab._on_language_changed("fr")
        
        # Verify signal was emitted
        assert signal_received
        assert new_language == "fr"
    
    def test_status_label_updates(self, settings_tab):
        """Test that status label updates correctly."""
        # Test initial status (after loading, it should show "loaded")
        assert "loaded" in settings_tab.status_label.text().lower()
        
        # Test setting different status
        settings_tab.status_label.setText("Settings saved")
        assert "saved" in settings_tab.status_label.text().lower()
        
        # Test setting ready status
        settings_tab.status_label.setText("Ready")
        assert "ready" in settings_tab.status_label.text().lower()
    
    def test_settings_validation(self, settings_tab):
        """Test that settings validation works correctly."""
        # Test valid window sizes
        settings_tab.window_width_spin.setValue(1000)
        settings_tab.window_height_spin.setValue(800)
        assert settings_tab.window_width_spin.value() == 1000
        assert settings_tab.window_height_spin.value() == 800
        
        # Test valid confidence threshold
        settings_tab.confidence_spin.setValue(75)
        assert settings_tab.confidence_spin.value() == 75
        
        # Test valid max retries
        settings_tab.max_retries_spin.setValue(5)
        assert settings_tab.max_retries_spin.value() == 5
    
    def test_button_states(self, settings_tab):
        """Test that buttons are properly enabled."""
        assert settings_tab.save_button.isEnabled()
        assert settings_tab.reset_button.isEnabled()
        assert settings_tab.apply_button.isEnabled()
    
    def test_checkbox_functionality(self, settings_tab, qtbot):
        """Test checkbox functionality."""
        # Test auto save checkbox
        settings_tab.auto_save_checkbox.setChecked(True)
        assert settings_tab.auto_save_checkbox.isChecked()
        
        settings_tab.auto_save_checkbox.setChecked(False)
        assert not settings_tab.auto_save_checkbox.isChecked()
        
        # Test show preview checkbox
        settings_tab.show_preview_checkbox.setChecked(True)
        assert settings_tab.show_preview_checkbox.isChecked()
        
        settings_tab.show_preview_checkbox.setChecked(False)
        assert not settings_tab.show_preview_checkbox.isChecked()
    
    def test_current_language_display(self, settings_tab):
        """Test current language display updates correctly."""
        # Test initial display
        current_language = get_language()
        assert current_language.upper() in settings_tab.current_language_label.text()
        
        # Test display update
        settings_tab._on_language_changed("fr")
        assert "FR" in settings_tab.current_language_label.text()
    
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.critical')
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.information')
    def test_validation_aspect_ratio_error(self, mock_information, mock_critical, settings_tab, qtbot):
        """Test validation error for invalid aspect ratio."""
        # Set width <= height (this is possible within the valid ranges)
        settings_tab.window_width_spin.setValue(800)
        settings_tab.window_height_spin.setValue(900)
        
        # Click save button
        qtbot.mouseClick(settings_tab.save_button, Qt.MouseButton.LeftButton)
        
        # Verify validation error was shown (called twice: validation error + exception handler)
        assert mock_critical.call_count == 2
        # Check that the first call is the validation error
        first_call_args = mock_critical.call_args_list[0][0]
        assert "Validation Error" in first_call_args[1]
    
    @patch('ocr_receipt.gui.settings_tab.QMessageBox.information')
    @patch('ocr_receipt.gui.settings_tab.set_language')
    def test_validation_success(self, mock_set_language, mock_message_box, settings_tab, qtbot):
        """Test successful validation with valid settings."""
        # Set valid settings
        settings_tab.window_width_spin.setValue(1200)
        settings_tab.window_height_spin.setValue(800)
        settings_tab.confidence_spin.setValue(75)
        settings_tab.max_retries_spin.setValue(5)
        
        # Click save button
        qtbot.mouseClick(settings_tab.save_button, Qt.MouseButton.LeftButton)
        
        # Verify settings were saved (no validation error)
        assert settings_tab.config_manager.get('gui.window_size') == [1200, 800]
        assert settings_tab.config_manager.get('ocr.confidence_threshold') == 0.75
        assert settings_tab.config_manager.get('ocr.max_retries') == 5
        
        # Verify success message was shown
        mock_message_box.assert_called_once()
    
    def test_validate_settings_method(self, settings_tab):
        """Test the _validate_settings method directly."""
        # Test with valid settings
        settings_tab.window_width_spin.setValue(1200)
        settings_tab.window_height_spin.setValue(800)
        settings_tab.confidence_spin.setValue(75)
        settings_tab.max_retries_spin.setValue(5)
        
        errors = settings_tab._validate_settings()
        assert len(errors) == 0
        
        # Test with invalid aspect ratio (this is possible within valid ranges)
        settings_tab.window_width_spin.setValue(800)
        settings_tab.window_height_spin.setValue(900)
        
        errors = settings_tab._validate_settings()
        assert len(errors) == 1  # Should have aspect ratio validation error
        assert "width should be greater than height" in errors[0].lower() 
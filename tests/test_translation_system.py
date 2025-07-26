"""
Unit tests for the translation system.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ocr_receipt.utils.translation_helper import (
    TranslationHelper, 
    get_translation_helper, 
    tr, 
    set_language, 
    get_language
)


class TestTranslationHelper:
    """Test the TranslationHelper class."""
    
    def test_singleton_pattern(self):
        """Test that TranslationHelper follows singleton pattern."""
        helper1 = TranslationHelper()
        helper2 = TranslationHelper()
        assert helper1 is helper2
    
    def test_default_language(self):
        """Test default language is English."""
        helper = TranslationHelper()
        assert helper.get_language() == 'en'
    
    def test_set_language_valid(self):
        """Test setting a valid language."""
        helper = TranslationHelper()
        assert helper.set_language('fr') is True
        assert helper.get_language() == 'fr'
    
    def test_set_language_invalid(self):
        """Test setting an invalid language."""
        helper = TranslationHelper()
        # Reset to English first
        helper.set_language('en')
        assert helper.set_language('invalid') is False
        assert helper.get_language() == 'en'  # Should remain default
    
    def test_get_available_languages(self):
        """Test getting available languages."""
        helper = TranslationHelper()
        languages = helper.get_available_languages()
        assert len(languages) == 2
        assert {'code': 'en', 'name': 'English'} in languages
        assert {'code': 'fr', 'name': 'Français'} in languages


class TestTranslationFunctions:
    """Test the convenience functions."""
    
    def test_get_translation_helper(self):
        """Test getting the global translation helper."""
        helper = get_translation_helper()
        assert isinstance(helper, TranslationHelper)
    
    def test_tr_function(self):
        """Test the tr function."""
        set_language('en')
        assert tr('main_window.title') == 'OCR Invoice Parser'
        assert tr('common.success') == 'Success'
    
    def test_tr_function_french(self):
        """Test the tr function with French."""
        set_language('fr')
        assert tr('main_window.title') == 'Analyseur de Factures OCR'
        assert tr('common.success') == 'Succès'
    
    def test_tr_function_parameters(self):
        """Test the tr function with parameters."""
        set_language('en')
        result = tr('business_keywords_tab.delete_confirm', count=5)
        assert '5' in result
        assert 'keyword(s)' in result
    
    def test_tr_function_missing_key(self):
        """Test the tr function with missing key."""
        set_language('en')
        result = tr('nonexistent.key')
        assert result == 'nonexistent.key'
    
    def test_set_language_function(self):
        """Test the set_language function."""
        assert set_language('en') is True
        assert get_language() == 'en'
        assert set_language('fr') is True
        assert get_language() == 'fr'
    
    def test_get_language_function(self):
        """Test the get_language function."""
        set_language('en')
        assert get_language() == 'en'
        set_language('fr')
        assert get_language() == 'fr'


class TestTranslationFiles:
    """Test translation file loading."""
    
    def test_translation_file_structure(self):
        """Test that translation files have the expected structure."""
        set_language('en')
        helper = get_translation_helper()
        
        # Check that key sections exist
        assert 'main_window' in helper._translations
        assert 'business_keywords_tab' in helper._translations
        assert 'common' in helper._translations
        assert 'add_business_dialog' in helper._translations
    
    def test_french_translation_file_structure(self):
        """Test that French translation file has the expected structure."""
        set_language('fr')
        helper = get_translation_helper()
        
        # Check that key sections exist
        assert 'main_window' in helper._translations
        assert 'business_keywords_tab' in helper._translations
        assert 'common' in helper._translations
        assert 'add_business_dialog' in helper._translations
    
    def test_translation_completeness(self):
        """Test that both languages have the same keys."""
        set_language('en')
        helper_en = get_translation_helper()
        en_keys = self._get_all_keys(helper_en._translations)
        
        set_language('fr')
        helper_fr = get_translation_helper()
        fr_keys = self._get_all_keys(helper_fr._translations)
        
        # Both languages should have the same keys
        assert set(en_keys) == set(fr_keys)
    
    def _get_all_keys(self, translations, prefix=''):
        """Helper method to get all keys from a translation dictionary."""
        keys = []
        for key, value in translations.items():
            current_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                keys.extend(self._get_all_keys(value, current_key))
            else:
                keys.append(current_key)
        return keys


class TestTranslationIntegration:
    """Test translation integration with the application."""
    
    def test_main_window_title_translation(self, qtbot):
        """Test that main window title is translated."""
        from ocr_receipt.utils.translation_helper import tr, set_language
        
        # Test English
        set_language('en')
        assert tr('main_window.title') == 'OCR Invoice Parser'
        
        # Test French
        set_language('fr')
        assert tr('main_window.title') == 'Analyseur de Factures OCR'
    
    def test_business_keywords_tab_translation(self, qtbot):
        """Test that business keywords tab uses translations."""
        set_language('en')
        from ocr_receipt.business.database_manager import DatabaseManager
        from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
        from ocr_receipt.gui.business_keywords_tab import BusinessKeywordsTab
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db_manager = None
        try:
            db_manager = DatabaseManager(db_path)
            business_mapping_manager = BusinessMappingManager(db_manager)
            tab = BusinessKeywordsTab(business_mapping_manager)
            qtbot.addWidget(tab)
            
            assert tab.add_button.text() == 'Add Business'
            assert tab.edit_button.text() == 'Edit Keyword'
            assert tab.delete_button.text() == 'Delete Keyword'
            
        finally:
            if db_manager:
                db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass  # File might already be deleted or locked
    
    def test_add_business_dialog_translation(self, qtbot):
        """Test that add business dialog uses translations."""
        set_language('en')
        from ocr_receipt.gui.dialogs.add_business_dialog import AddBusinessDialog
        
        dialog = AddBusinessDialog()
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == 'Add Business'
        assert dialog.ok_button.text() == 'Add Business'
        assert dialog.cancel_button.text() == 'Cancel' 
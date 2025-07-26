"""
Language Manager for OCR Receipt Parser.

Handles internationalization (i18n) for the application, supporting
French and English languages with fallback mechanisms.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

class LanguageManager:
    """
    Manages application internationalization and translations.
    """
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'fr': 'Français'
    }
    
    DEFAULT_LANGUAGE = 'en'
    
    def __init__(self, language: str = None, translations_path: str = None):
        """
        Initialize the language manager.
        
        :param language: Language code (e.g., 'en', 'fr')
        :param translations_path: Path to translations directory
        """
        self.logger = logging.getLogger(__name__)
        self.current_language = language or self.DEFAULT_LANGUAGE
        self.translations_path = translations_path or self._get_default_translations_path()
        self.translations = {}
        self.fallback_translations = {}
        
        # Load translations
        self._load_translations()
    
    def _get_default_translations_path(self) -> str:
        """Get the default path for translation files."""
        # Look for translations in the utils directory
        utils_dir = Path(__file__).parent
        translations_dir = utils_dir / 'translations'
        
        # Create directory if it doesn't exist
        translations_dir.mkdir(exist_ok=True)
        
        return str(translations_dir)
    
    def _load_translations(self) -> None:
        """Load translation files for current and fallback languages."""
        try:
            # Load current language translations
            current_file = os.path.join(self.translations_path, f'{self.current_language}.json')
            if os.path.exists(current_file):
                with open(current_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            else:
                self.logger.warning(f"Translation file not found: {current_file}")
                self.translations = {}
            
            # Load fallback language translations (English)
            if self.current_language != self.DEFAULT_LANGUAGE:
                fallback_file = os.path.join(self.translations_path, f'{self.DEFAULT_LANGUAGE}.json')
                if os.path.exists(fallback_file):
                    with open(fallback_file, 'r', encoding='utf-8') as f:
                        self.fallback_translations = json.load(f)
                else:
                    self.logger.warning(f"Fallback translation file not found: {fallback_file}")
                    self.fallback_translations = {}
            else:
                self.fallback_translations = self.translations
                
        except Exception as e:
            self.logger.error(f"Error loading translations: {e}")
            self.translations = {}
            self.fallback_translations = {}
    
    def set_language(self, language: str) -> bool:
        """
        Set the current language.
        
        :param language: Language code (e.g., 'en', 'fr')
        :return: True if language was set successfully, False otherwise
        """
        if language not in self.SUPPORTED_LANGUAGES:
            self.logger.error(f"Unsupported language: {language}")
            return False
        
        if language != self.current_language:
            self.current_language = language
            self._load_translations()
            self.logger.info(f"Language changed to: {self.SUPPORTED_LANGUAGES[language]}")
        
        return True
    
    def get_language_name(self, language_code: str = None) -> str:
        """
        Get the display name for a language code.
        
        :param language_code: Language code (e.g., 'en', 'fr')
        :return: Language display name
        """
        code = language_code or self.current_language
        return self.SUPPORTED_LANGUAGES.get(code, code)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get all supported languages.
        
        :return: Dictionary of language codes to display names
        """
        return self.SUPPORTED_LANGUAGES.copy()
    
    def get_current_language(self) -> str:
        """
        Get the current language code.
        
        :return: Current language code
        """
        return self.current_language
    
    def tr(self, key: str, **kwargs) -> str:
        """
        Translate a key to the current language.
        
        :param key: Translation key (dot notation supported for nested keys)
        :param kwargs: Format parameters for the translation
        :return: Translated string
        """
        # Get translation from current language
        translation = self._get_nested_translation(self.translations, key)
        
        # Fallback to default language if not found
        if translation is None:
            translation = self._get_nested_translation(self.fallback_translations, key)
        
        # Fallback to key itself if still not found
        if translation is None:
            self.logger.warning(f"Translation key not found: {key}")
            translation = key
        
        # Format the translation with provided parameters
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError) as e:
            self.logger.error(f"Error formatting translation for key '{key}': {e}")
            return translation
    
    def _get_nested_translation(self, translations: Dict[str, Any], key: str) -> Optional[str]:
        """
        Get a nested translation value using dot notation.
        
        :param translations: Translation dictionary
        :param key: Translation key (dot notation supported)
        :return: Translation value or None if not found
        """
        keys = key.split('.')
        value = translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return str(value) if value is not None else None
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """
        Get list of available languages with their display names.
        
        :return: List of language dictionaries with 'code' and 'name' keys
        """
        return [
            {'code': code, 'name': name}
            for code, name in self.SUPPORTED_LANGUAGES.items()
        ]
    
    def create_translation_file(self, language: str) -> bool:
        """
        Create a new translation file for a language.
        
        :param language: Language code
        :return: True if file was created successfully
        """
        if language not in self.SUPPORTED_LANGUAGES:
            self.logger.error(f"Cannot create translation file for unsupported language: {language}")
            return False
        
        file_path = os.path.join(self.translations_path, f'{language}.json')
        
        if os.path.exists(file_path):
            self.logger.warning(f"Translation file already exists: {file_path}")
            return False
        
        try:
            # Create empty translation file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Created translation file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating translation file: {e}")
            return False
    
    def reload_translations(self) -> None:
        """Reload translation files from disk."""
        self._load_translations()
        self.logger.info("Translations reloaded")
    
    def get_missing_translations(self) -> List[str]:
        """
        Get list of translation keys that are missing in the current language.
        
        :return: List of missing translation keys
        """
        missing = []
        
        # Get all keys from fallback language
        fallback_keys = self._get_all_keys(self.fallback_translations)
        
        for key in fallback_keys:
            if self._get_nested_translation(self.translations, key) is None:
                missing.append(key)
        
        return missing
    
    def _get_all_keys(self, translations: Dict[str, Any], prefix: str = '') -> List[str]:
        """
        Get all translation keys from a translation dictionary.
        
        :param translations: Translation dictionary
        :param prefix: Current key prefix
        :return: List of all translation keys
        """
        keys = []
        
        for key, value in translations.items():
            current_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                keys.extend(self._get_all_keys(value, current_key))
            else:
                keys.append(current_key)
        
        return keys 
"""
Translation Helper for OCR Receipt Parser.

Provides easy access to translations throughout the application.
"""

import os
import json
from typing import Optional
from pathlib import Path

class TranslationHelper:
    """
    Simple translation helper for the application.
    """
    
    _instance = None
    _translations = {}
    _current_language = 'en'
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranslationHelper, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._load_translations()
            self._initialized = True
    
    def _get_translations_path(self) -> str:
        """Get the path to translation files."""
        utils_dir = Path(__file__).parent
        translations_dir = utils_dir / 'translations'
        return str(translations_dir)
    
    def _load_translations(self) -> None:
        """Load translations for the current language."""
        translations_path = self._get_translations_path()
        translation_file = os.path.join(translations_path, f'{self._current_language}.json')
        
        if os.path.exists(translation_file):
            try:
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self._translations = json.load(f)
            except Exception as e:
                print(f"Error loading translations: {e}")
                self._translations = {}
        else:
            print(f"Translation file not found: {translation_file}")
            self._translations = {}
    
    def set_language(self, language: str) -> bool:
        """
        Set the current language.
        
        :param language: Language code ('en' or 'fr')
        :return: True if language was set successfully
        """
        if language not in ['en', 'fr']:
            print(f"Unsupported language: {language}")
            return False
        
        if language != self._current_language:
            self._current_language = language
            self._load_translations()
        
        return True
    
    def get_language(self) -> str:
        """Get the current language code."""
        return self._current_language
    
    def tr(self, key: str, **kwargs) -> str:
        """
        Translate a key to the current language.
        
        :param key: Translation key (dot notation supported)
        :param kwargs: Format parameters
        :return: Translated string
        """
        # Get translation using dot notation
        keys = key.split('.')
        value = self._translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # Fallback to key itself
                return key
        
        if value is None:
            return key
        
        # Format the translation with provided parameters
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            return str(value)
    
    def get_available_languages(self) -> list:
        """Get list of available languages."""
        return [
            {'code': 'en', 'name': 'English'},
            {'code': 'fr', 'name': 'Français'}
        ]

# Global instance
_translation_helper = None

def get_translation_helper() -> TranslationHelper:
    """Get the global translation helper instance."""
    global _translation_helper
    if _translation_helper is None:
        _translation_helper = TranslationHelper()
    return _translation_helper

def tr(key: str, **kwargs) -> str:
    """
    Convenience function to translate a key.
    
    :param key: Translation key
    :param kwargs: Format parameters
    :return: Translated string
    """
    return get_translation_helper().tr(key, **kwargs)

def set_language(language: str) -> bool:
    """
    Convenience function to set the language.
    
    :param language: Language code ('en' or 'fr')
    :return: True if language was set successfully
    """
    return get_translation_helper().set_language(language)

def get_language() -> str:
    """
    Convenience function to get the current language.
    
    :return: Current language code
    """
    return get_translation_helper().get_language() 
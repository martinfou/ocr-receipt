"""
Language Settings Dialog for OCR Receipt Parser.

Allows users to change the application language.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from typing import Optional
from ...utils.translation_helper import tr, set_language, get_language, get_translation_helper

class LanguageSettingsDialog(QDialog):
    """
    Dialog for changing application language.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("language_settings.title"))
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.selected_language = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(tr("language_settings.header"))
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(tr("language_settings.description"))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(desc_label)
        
        # Language selection
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel(tr("language_settings.language_label")))
        
        self.language_combo = QComboBox()
        self._populate_languages()
        language_layout.addWidget(self.language_combo)
        layout.addLayout(language_layout)
        
        # Current language info
        current_language = get_language()
        current_language_name = self._get_language_name(current_language)
        current_label = QLabel(tr("language_settings.current_language", 
                                 language=current_language_name))
        current_label.setStyleSheet("color: #666; font-style: italic; margin-top: 10px;")
        layout.addWidget(current_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton(tr("common.cancel"))
        self.apply_button = QPushButton(tr("language_settings.apply"))
        self.apply_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        layout.addLayout(button_layout)
        
        # Connect signals
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self._on_apply)
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
        
        # Set initial selection
        self._set_current_language_selection()
    
    def _populate_languages(self):
        """Populate the language combo box."""
        languages = get_translation_helper().get_available_languages()
        for lang in languages:
            self.language_combo.addItem(lang['name'], lang['code'])
    
    def _get_language_name(self, language_code: str) -> str:
        """Get the display name for a language code."""
        languages = get_translation_helper().get_available_languages()
        for lang in languages:
            if lang['code'] == language_code:
                return lang['name']
        return language_code
    
    def _set_current_language_selection(self):
        """Set the combo box to show the current language."""
        current_language = get_language()
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_language:
                self.language_combo.setCurrentIndex(i)
                break
    
    def _on_language_changed(self, language_name: str):
        """Handle language selection change."""
        # Find the language code for the selected name
        for i in range(self.language_combo.count()):
            if self.language_combo.itemText(i) == language_name:
                self.selected_language = self.language_combo.itemData(i)
                break
    
    def _on_apply(self):
        """Handle apply button click."""
        if self.selected_language and self.selected_language != get_language():
            # Apply the language change
            success = set_language(self.selected_language)
            if success:
                QMessageBox.information(
                    self,
                    tr("common.success"),
                    tr("language_settings.language_changed", 
                       language=self._get_language_name(self.selected_language))
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    tr("common.error"),
                    tr("language_settings.language_change_failed")
                )
        else:
            # No change needed
            self.accept()
    
    def get_selected_language(self) -> Optional[str]:
        """Get the selected language code."""
        return self.selected_language 
"""
SettingsTab: Application settings and configuration interface.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QFormLayout, QGroupBox, QSpinBox, QCheckBox,
    QLineEdit, QMessageBox, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional, Dict, Any
from datetime import datetime
import os
from ..config import ConfigManager
from ..utils.translation_helper import tr, set_language, get_language
import logging

logger = logging.getLogger(__name__)

class SettingsTab(QWidget):
    """Main settings management tab."""
    
    language_changed = pyqtSignal(str)  # Emits new language code when changed
    
    def __init__(self, config_manager: ConfigManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.config_manager = config_manager
        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self) -> None:
        """Setup the main UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header section
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel(tr("settings_tab.title"))
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(tr("settings_tab.subtitle"))
        subtitle_label.setStyleSheet("color: #666;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Language Settings Group
        language_group = QGroupBox(tr("settings_tab.language_group"))
        language_layout = QFormLayout(language_group)
        
        # Language dropdown
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Français", "fr")
        # Don't connect to currentTextChanged - only change language on Apply/Save
        language_layout.addRow(tr("settings_tab.language_label"), self.language_combo)
        
        # Current language display
        self.current_language_label = QLabel()
        self.current_language_label.setStyleSheet("color: #666; font-style: italic;")
        language_layout.addRow(tr("settings_tab.current_language"), self.current_language_label)
        
        layout.addWidget(language_group)
        
        # GUI Settings Group
        gui_group = QGroupBox(tr("settings_tab.gui_group"))
        gui_layout = QFormLayout(gui_group)
        
        # Window size settings
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 2000)
        self.window_width_spin.setSuffix(" px")
        gui_layout.addRow(tr("settings_tab.window_width"), self.window_width_spin)
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 1500)
        self.window_height_spin.setSuffix(" px")
        gui_layout.addRow(tr("settings_tab.window_height"), self.window_height_spin)
        
        # Auto-save setting
        self.auto_save_checkbox = QCheckBox()
        gui_layout.addRow(tr("settings_tab.auto_save"), self.auto_save_checkbox)
        
        # Show preview setting
        self.show_preview_checkbox = QCheckBox()
        gui_layout.addRow(tr("settings_tab.show_preview"), self.show_preview_checkbox)
        
        layout.addWidget(gui_group)
        
        # OCR Settings Group
        ocr_group = QGroupBox(tr("settings_tab.ocr_group"))
        ocr_layout = QFormLayout(ocr_group)
        
        # Confidence threshold
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(10, 100)
        self.confidence_spin.setSuffix("%")
        ocr_layout.addRow(tr("settings_tab.confidence_threshold"), self.confidence_spin)
        
        # Max retries
        self.max_retries_spin = QSpinBox()
        self.max_retries_spin.setRange(1, 10)
        ocr_layout.addRow(tr("settings_tab.max_retries"), self.max_retries_spin)
        
        layout.addWidget(ocr_group)
        
        # Database Settings Group
        db_group = QGroupBox(tr("settings_tab.database_group"))
        db_layout = QFormLayout(db_group)
        
        # Database path
        db_path_layout = QHBoxLayout()
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setReadOnly(True)
        self.db_browse_button = QPushButton(tr("settings_tab.browse_button"))
        self.db_browse_button.clicked.connect(self._on_browse_database)
        
        db_path_layout.addWidget(self.db_path_edit)
        db_path_layout.addWidget(self.db_browse_button)
        db_layout.addRow(tr("settings_tab.database_path"), db_path_layout)
        
        # Database backup section
        backup_layout = QHBoxLayout()
        self.backup_button = QPushButton(tr("settings_tab.backup_database"))
        self.backup_button.clicked.connect(self._on_backup_database)
        
        self.restore_button = QPushButton(tr("settings_tab.restore_database"))
        self.restore_button.clicked.connect(self._on_restore_database)
        
        backup_layout.addWidget(self.backup_button)
        backup_layout.addWidget(self.restore_button)
        db_layout.addRow(tr("settings_tab.database_backup"), backup_layout)
        
        layout.addWidget(db_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton(tr("settings_tab.save_button"))
        self.save_button.clicked.connect(self._on_save_settings)
        
        self.reset_button = QPushButton(tr("settings_tab.reset_button"))
        self.reset_button.clicked.connect(self._on_reset_settings)
        
        self.apply_button = QPushButton(tr("settings_tab.apply_button"))
        self.apply_button.clicked.connect(self._on_apply_settings)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Status bar
        self.status_label = QLabel(tr("settings_tab.status_ready"))
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def _load_current_settings(self) -> None:
        """Load current settings from config manager."""
        try:
            # Language settings
            current_language = get_language()
            index = self.language_combo.findData(current_language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
            
            self.current_language_label.setText(tr("settings_tab.current_language_display").format(language=current_language.upper()))
            
            # GUI settings
            window_size = self.config_manager.get('gui.window_size', [1200, 800])
            self.window_width_spin.setValue(window_size[0])
            self.window_height_spin.setValue(window_size[1])
            
            self.auto_save_checkbox.setChecked(self.config_manager.get('gui.auto_save', True))
            self.show_preview_checkbox.setChecked(self.config_manager.get('gui.show_preview', True))
            
            # OCR settings
            confidence = int(self.config_manager.get('ocr.confidence_threshold', 0.6) * 100)
            self.confidence_spin.setValue(confidence)
            
            self.max_retries_spin.setValue(self.config_manager.get('ocr.max_retries', 3))
            
            # Database settings
            db_path = self.config_manager.get('database.path', 'ocr_receipts.db')
            self.db_path_edit.setText(db_path)
            
            self.status_label.setText(tr("settings_tab.status_loaded"))
            
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self.status_label.setText(tr("settings_tab.status_error"))

    def _on_language_changed(self, language_code: str) -> None:
        """Handle language change and emit signal."""
        # Update the current language display
        self.current_language_label.setText(tr("settings_tab.current_language_display").format(language=language_code.upper()))
        
        # Emit signal for language change
        self.language_changed.emit(language_code)

    def _on_save_settings(self) -> None:
        """Handle save settings button click."""
        try:
            # Save all settings
            self._save_current_settings()
            
            # Apply language change if needed
            current_language = get_language()
            selected_index = self.language_combo.currentIndex()
            if selected_index >= 0:
                selected_language = self.language_combo.itemData(selected_index)
                if selected_language != current_language:
                    set_language(selected_language)
                    self.config_manager.set('app.ui_language', selected_language)
                    # Emit signal to update UI
                    self._on_language_changed(selected_language)
            
            self.status_label.setText(tr("settings_tab.status_saved"))
            QMessageBox.information(self, tr("settings_tab.save_success_title"), 
                                  tr("settings_tab.save_success_message"))
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, tr("settings_tab.save_error_title"), 
                               tr("settings_tab.save_error_message").format(error=str(e)))

    def _on_apply_settings(self) -> None:
        """Handle apply settings button click."""
        try:
            # Apply language change immediately
            selected_index = self.language_combo.currentIndex()
            if selected_index >= 0:
                selected_language = self.language_combo.itemData(selected_index)
                current_language = get_language()
                
                if selected_language != current_language:
                    set_language(selected_language)
                    self.config_manager.set('app.ui_language', selected_language)
                    # Emit signal to update UI
                    self._on_language_changed(selected_language)
                    
                    QMessageBox.information(self, tr("settings_tab.language_changed_title"), 
                                          tr("settings_tab.language_changed_message").format(language=selected_language.upper()))
            
            self.status_label.setText(tr("settings_tab.status_applied"))
            
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            QMessageBox.critical(self, tr("settings_tab.apply_error_title"), 
                               tr("settings_tab.apply_error_message").format(error=str(e)))

    def _on_reset_settings(self) -> None:
        """Handle reset settings button click."""
        reply = QMessageBox.question(
            self,
            tr("settings_tab.reset_confirm_title"),
            tr("settings_tab.reset_confirm_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._load_current_settings()
                self.status_label.setText(tr("settings_tab.status_reset"))
            except Exception as e:
                logger.error(f"Failed to reset settings: {e}")
                QMessageBox.critical(self, tr("settings_tab.reset_error_title"), 
                                   tr("settings_tab.reset_error_message").format(error=str(e)))

    def _save_current_settings(self) -> None:
        """Save current UI settings to config manager."""
        # Validate settings before saving
        validation_errors = self._validate_settings()
        if validation_errors:
            error_message = "\n".join(validation_errors)
            QMessageBox.critical(self, tr("settings_tab.validation_error_title"), 
                               tr("settings_tab.validation_error_message").format(error=error_message))
            raise ValueError(f"Validation failed: {error_message}")
        
        # GUI settings
        window_width = self.window_width_spin.value()
        window_height = self.window_height_spin.value()
        self.config_manager.set('gui.window_size', [window_width, window_height])
        
        self.config_manager.set('gui.auto_save', self.auto_save_checkbox.isChecked())
        self.config_manager.set('gui.show_preview', self.show_preview_checkbox.isChecked())
        
        # OCR settings
        confidence = self.confidence_spin.value() / 100.0
        self.config_manager.set('ocr.confidence_threshold', confidence)
        
        self.config_manager.set('ocr.max_retries', self.max_retries_spin.value())
        
        # Save config to file
        self.config_manager.save()
    
    def _validate_settings(self) -> list:
        """Validate current settings and return list of error messages."""
        errors = []
        
        # Validate window size
        window_width = self.window_width_spin.value()
        window_height = self.window_height_spin.value()
        
        if window_width < 800 or window_width > 2000:
            errors.append(tr("settings_tab.validation_window_width"))
        
        if window_height < 600 or window_height > 1500:
            errors.append(tr("settings_tab.validation_window_height"))
        
        # Validate aspect ratio (width should be greater than height for typical desktop)
        if window_width <= window_height:
            errors.append(tr("settings_tab.validation_aspect_ratio"))
        
        # Validate confidence threshold
        confidence = self.confidence_spin.value()
        if confidence < 10 or confidence > 100:
            errors.append(tr("settings_tab.validation_confidence"))
        
        # Validate max retries
        max_retries = self.max_retries_spin.value()
        if max_retries < 1 or max_retries > 10:
            errors.append(tr("settings_tab.validation_max_retries"))
        
        return errors
    
    def _on_browse_database(self) -> None:
        """Handle browse button click for database path."""
        current_path = self.db_path_edit.text()
        
        # Open file dialog to select database file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("settings_tab.select_database_title"),
            current_path,
            tr("settings_tab.database_file_filter")
        )
        
        if file_path:
            self.db_path_edit.setText(file_path)
            # Update the config manager
            self.config_manager.set('database.path', file_path)
            self.status_label.setText(tr("settings_tab.database_path_updated"))
    
    def _on_backup_database(self) -> None:
        """Handle backup database button click."""
        current_db_path = self.db_path_edit.text()
        
        if not current_db_path or not os.path.exists(current_db_path):
            QMessageBox.warning(self, tr("settings_tab.backup_error_title"),
                              tr("settings_tab.backup_no_database"))
            return
        
        # Open file dialog to select backup location
        backup_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("settings_tab.select_backup_title"),
            f"{current_db_path}.backup",
            tr("settings_tab.database_file_filter")
        )
        
        if backup_path:
            try:
                import shutil
                shutil.copy2(current_db_path, backup_path)
                QMessageBox.information(self, tr("settings_tab.backup_success_title"),
                                      tr("settings_tab.backup_success_message").format(path=backup_path))
                self.status_label.setText(tr("settings_tab.backup_created"))
            except Exception as e:
                QMessageBox.critical(self, tr("settings_tab.backup_error_title"),
                                   tr("settings_tab.backup_error_message").format(error=str(e)))
    
    def _on_restore_database(self) -> None:
        """Handle restore database button click."""
        current_db_path = self.db_path_edit.text()
        
        # Open file dialog to select backup file
        backup_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("settings_tab.select_restore_title"),
            "",
            tr("settings_tab.database_file_filter")
        )
        
        if backup_path:
            reply = QMessageBox.question(
                self,
                tr("settings_tab.restore_confirm_title"),
                tr("settings_tab.restore_confirm_message").format(path=backup_path),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    import shutil
                    # Create a backup of current database before restoring
                    if current_db_path and os.path.exists(current_db_path):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        current_backup = f"{current_db_path}.before_restore_{timestamp}"
                        shutil.copy2(current_db_path, current_backup)
                    
                    # Restore the selected backup
                    shutil.copy2(backup_path, current_db_path)
                    QMessageBox.information(self, tr("settings_tab.restore_success_title"),
                                          tr("settings_tab.restore_success_message"))
                    self.status_label.setText(tr("settings_tab.database_restored"))
                except Exception as e:
                    QMessageBox.critical(self, tr("settings_tab.restore_error_title"),
                                       tr("settings_tab.restore_error_message").format(error=str(e))) 
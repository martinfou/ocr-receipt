"""
Tests for PDF loading visual indicators in the SinglePDFTab.

This test file covers:
- Progress bar visibility during processing
- Status label updates for different stages
- Control enabling/disabling during processing
- Error handling with visual feedback
"""

import pytest
import tempfile
import os
from PyQt6.QtCore import Qt

from ocr_receipt.gui.single_pdf_tab import SinglePDFTab
from ocr_receipt.business.database_manager import DatabaseManager
from ocr_receipt.business.business_mapping_manager import BusinessMappingManager
from ocr_receipt.business.project_manager import ProjectManager
from ocr_receipt.business.category_manager import CategoryManager


class TestPDFLoadingIndicators:
    """Test the PDF loading visual indicators."""
    
    @pytest.fixture
    def single_pdf_tab(self, qapp, qtbot):
        """Create a SinglePDFTab for testing."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            db_manager.initialize_database()
            business_mapping_manager = BusinessMappingManager(db_manager)
            project_manager = ProjectManager(db_manager)
            category_manager = CategoryManager(db_manager)
            
            tab = SinglePDFTab(
                business_mapping_manager=business_mapping_manager,
                project_manager=project_manager,
                category_manager=category_manager
            )
            qtbot.addWidget(tab)
            yield tab
            
        finally:
            db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass
    
    def test_progress_indicator_creation(self, single_pdf_tab):
        """Test that progress indicators are created correctly."""
        assert hasattr(single_pdf_tab, 'progress_bar')
        assert hasattr(single_pdf_tab, 'status_label')
        assert single_pdf_tab.progress_bar is not None
        assert single_pdf_tab.status_label is not None
    
    def test_initial_state(self, single_pdf_tab):
        """Test initial state of progress indicators."""
        # Progress bar should be hidden initially
        assert not single_pdf_tab.progress_bar.isVisible()
        
        # Status label should show ready message
        assert "Ready" in single_pdf_tab.status_label.text()
        
        # All controls should be enabled initially
        assert single_pdf_tab.browse_rename_button.isEnabled()
        assert single_pdf_tab.rename_button.isEnabled()
        assert single_pdf_tab.raw_data_button.isEnabled()
        assert single_pdf_tab.ocr_button.isEnabled()
    
    def test_processing_stage_loading(self, single_pdf_tab, qtbot):
        """Test loading stage visual feedback."""
        single_pdf_tab.show_processing_stage("loading")
        qtbot.wait(10)  # Process events
        
        # Status should show loading message
        assert "Loading PDF file" in single_pdf_tab.status_label.text()
        
        # Controls should be disabled
        assert not single_pdf_tab.browse_rename_button.isEnabled()
        assert not single_pdf_tab.rename_button.isEnabled()
        assert not single_pdf_tab.raw_data_button.isEnabled()
        assert not single_pdf_tab.ocr_button.isEnabled()
        
        # Progress bar should be configured for indeterminate progress
        assert single_pdf_tab.progress_bar.minimum() == 0
        assert single_pdf_tab.progress_bar.maximum() == 0  # Indeterminate
    
    def test_processing_stage_converting(self, single_pdf_tab, qtbot):
        """Test converting stage visual feedback."""
        single_pdf_tab.show_processing_stage("converting")
        qtbot.wait(10)  # Process events
        
        # Status should show converting message
        assert "Converting pages" in single_pdf_tab.status_label.text()
        
        # Controls should be disabled
        assert not single_pdf_tab.browse_rename_button.isEnabled()
        assert not single_pdf_tab.rename_button.isEnabled()
        assert not single_pdf_tab.raw_data_button.isEnabled()
        assert not single_pdf_tab.ocr_button.isEnabled()
        
        # Progress bar should be configured for indeterminate progress
        assert single_pdf_tab.progress_bar.minimum() == 0
        assert single_pdf_tab.progress_bar.maximum() == 0  # Indeterminate
    
    def test_processing_stage_ocr(self, single_pdf_tab, qtbot):
        """Test OCR stage visual feedback."""
        single_pdf_tab.show_processing_stage("ocr")
        qtbot.wait(10)  # Process events
        
        # Status should show OCR message
        assert "Running OCR" in single_pdf_tab.status_label.text()
        
        # Controls should be disabled
        assert not single_pdf_tab.browse_rename_button.isEnabled()
        assert not single_pdf_tab.rename_button.isEnabled()
        assert not single_pdf_tab.raw_data_button.isEnabled()
        assert not single_pdf_tab.ocr_button.isEnabled()
        
        # Progress bar should be configured for indeterminate progress
        assert single_pdf_tab.progress_bar.minimum() == 0
        assert single_pdf_tab.progress_bar.maximum() == 0  # Indeterminate
    
    def test_processing_stage_extracting(self, single_pdf_tab, qtbot):
        """Test extracting stage visual feedback."""
        single_pdf_tab.show_processing_stage("extracting")
        qtbot.wait(10)  # Process events
        
        # Status should show extracting message
        assert "Extracting invoice data" in single_pdf_tab.status_label.text()
        
        # Controls should be disabled
        assert not single_pdf_tab.browse_rename_button.isEnabled()
        assert not single_pdf_tab.rename_button.isEnabled()
        assert not single_pdf_tab.raw_data_button.isEnabled()
        assert not single_pdf_tab.ocr_button.isEnabled()
        
        # Progress bar should be configured for indeterminate progress
        assert single_pdf_tab.progress_bar.minimum() == 0
        assert single_pdf_tab.progress_bar.maximum() == 0  # Indeterminate
    
    def test_processing_stage_matching(self, single_pdf_tab, qtbot):
        """Test matching stage visual feedback."""
        single_pdf_tab.show_processing_stage("matching")
        qtbot.wait(10)  # Process events
        
        # Status should show matching message
        assert "Matching business names" in single_pdf_tab.status_label.text()
        
        # Controls should be disabled
        assert not single_pdf_tab.browse_rename_button.isEnabled()
        assert not single_pdf_tab.rename_button.isEnabled()
        assert not single_pdf_tab.raw_data_button.isEnabled()
        assert not single_pdf_tab.ocr_button.isEnabled()
        
        # Progress bar should be configured for indeterminate progress
        assert single_pdf_tab.progress_bar.minimum() == 0
        assert single_pdf_tab.progress_bar.maximum() == 0  # Indeterminate
    
    def test_processing_stage_complete(self, single_pdf_tab):
        """Test complete stage visual feedback."""
        single_pdf_tab.show_processing_stage("complete")
        
        # Status should show complete message
        assert "Processing complete" in single_pdf_tab.status_label.text()
        
        # Controls should be enabled
        assert single_pdf_tab.browse_rename_button.isEnabled()
        assert single_pdf_tab.rename_button.isEnabled()
        assert single_pdf_tab.raw_data_button.isEnabled()
        assert single_pdf_tab.ocr_button.isEnabled()
    
    def test_processing_stage_error(self, single_pdf_tab):
        """Test error stage visual feedback."""
        single_pdf_tab.show_processing_stage("error")
        
        # Status should show error message
        assert "Error occurred" in single_pdf_tab.status_label.text()
        
        # Controls should be enabled (so user can retry)
        assert single_pdf_tab.browse_rename_button.isEnabled()
        assert single_pdf_tab.rename_button.isEnabled()
        assert single_pdf_tab.raw_data_button.isEnabled()
        assert single_pdf_tab.ocr_button.isEnabled()
    
    def test_unknown_processing_stage(self, single_pdf_tab, qtbot):
        """Test handling of unknown processing stage."""
        single_pdf_tab.show_processing_stage("unknown_stage")
        qtbot.wait(10)  # Process events
        
        # Should default to processing state
        assert "Processing" in single_pdf_tab.status_label.text()
        
        # Controls should be disabled
        assert not single_pdf_tab.browse_rename_button.isEnabled()
        assert not single_pdf_tab.rename_button.isEnabled()
        assert not single_pdf_tab.raw_data_button.isEnabled()
        assert not single_pdf_tab.ocr_button.isEnabled()
        
        # Progress bar should be configured for indeterminate progress
        assert single_pdf_tab.progress_bar.minimum() == 0
        assert single_pdf_tab.progress_bar.maximum() == 0  # Indeterminate
    
    def test_stage_transitions(self, single_pdf_tab, qtbot):
        """Test transitions between different processing stages."""
        # Start with loading
        single_pdf_tab.show_processing_stage("loading")
        qtbot.wait(10)  # Process events
        assert "Loading PDF file" in single_pdf_tab.status_label.text()
        
        # Transition to converting
        single_pdf_tab.show_processing_stage("converting")
        qtbot.wait(10)  # Process events
        assert "Converting pages" in single_pdf_tab.status_label.text()
        
        # Transition to OCR
        single_pdf_tab.show_processing_stage("ocr")
        qtbot.wait(10)  # Process events
        assert "Running OCR" in single_pdf_tab.status_label.text()
        
        # Transition to complete
        single_pdf_tab.show_processing_stage("complete")
        qtbot.wait(10)  # Process events
        assert "Processing complete" in single_pdf_tab.status_label.text()
        assert single_pdf_tab.browse_rename_button.isEnabled()
    
    def test_progress_bar_styling(self, single_pdf_tab):
        """Test that progress bar has appropriate styling."""
        # Check that progress bar exists and is properly configured
        assert single_pdf_tab.progress_bar is not None
        assert single_pdf_tab.progress_bar.maximumHeight() == 20
    
    def test_status_label_styling(self, single_pdf_tab):
        """Test that status label has appropriate styling."""
        # Check that status label has styling applied
        style_sheet = single_pdf_tab.status_label.styleSheet()
        assert "color" in style_sheet
        assert "font-style" in style_sheet


class TestPDFProcessingIntegration:
    """Test integration of visual indicators with PDF processing."""
    
    @pytest.fixture
    def single_pdf_tab(self, qapp, qtbot):
        """Create a SinglePDFTab for testing."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(db_path)
            db_manager.initialize_database()
            business_mapping_manager = BusinessMappingManager(db_manager)
            project_manager = ProjectManager(db_manager)
            category_manager = CategoryManager(db_manager)
            
            tab = SinglePDFTab(
                business_mapping_manager=business_mapping_manager,
                project_manager=project_manager,
                category_manager=category_manager
            )
            qtbot.addWidget(tab)
            yield tab
            
        finally:
            db_manager.close()
            try:
                os.unlink(db_path)
            except (OSError, PermissionError):
                pass
    
    def test_ocr_button_functionality(self, single_pdf_tab, qtbot):
        """Test that OCR button triggers processing with visual feedback."""
        # Set a file path
        single_pdf_tab.file_path_edit.setText("/test/path/file.pdf")

        # Mock the processing method to avoid actual file processing
        original_method = single_pdf_tab._process_pdf_file
        called = False

        def mock_process(file_path):
            nonlocal called
            called = True
            # Simulate processing stages
            single_pdf_tab.show_processing_stage("loading")
            single_pdf_tab.show_processing_stage("converting")
            single_pdf_tab.show_processing_stage("ocr")
            single_pdf_tab.show_processing_stage("extracting")
            single_pdf_tab.show_processing_stage("matching")
            single_pdf_tab.show_processing_stage("complete")

        single_pdf_tab._process_pdf_file = mock_process

        # Click the OCR button
        qtbot.mouseClick(single_pdf_tab.ocr_button, Qt.MouseButton.LeftButton)
        
        # Verify the processing method was called
        assert called
        
        # Verify final state
        assert "Processing complete" in single_pdf_tab.status_label.text()
        assert single_pdf_tab.browse_rename_button.isEnabled()
        assert single_pdf_tab.ocr_button.isEnabled()
        
        # Restore original method
        single_pdf_tab._process_pdf_file = original_method 
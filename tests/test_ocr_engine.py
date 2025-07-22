"""
Unit tests for OCR Engine module.

This module tests the OCREngine class functionality including
multi-page PDF processing, confidence scoring, and error handling.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from ocr_receipt.core.ocr_engine import OCREngine, OCREngineError


class TestOCREngine:
    """Test cases for OCREngine class."""
    
    @pytest.fixture
    def mock_config(self) -> Dict[str, Any]:
        """Create a mock configuration for testing."""
        return {
            'ocr': {
                'language': 'eng',
                'confidence_threshold': 0.6,
                'tesseract_config': '--psm 6',
                'batch_size': 5,
                'enable_parallel': False
            }
        }
    
    @pytest.fixture
    def ocr_engine(self, mock_config) -> OCREngine:
        """Create an OCREngine instance for testing."""
        with patch('ocr_receipt.core.ocr_engine.pytesseract.get_tesseract_version'):
            return OCREngine(mock_config)
    
    @pytest.fixture
    def mock_pdf_path(self) -> str:
        """Create a mock PDF file path."""
        return "/path/to/test.pdf"
    
    def test_init_valid_config(self, mock_config):
        """Test OCREngine initialization with valid config."""
        with patch('ocr_receipt.core.ocr_engine.pytesseract.get_tesseract_version'):
            engine = OCREngine(mock_config)
            
            assert engine.language == 'eng'
            assert engine.confidence_threshold == 0.6
            assert engine.tesseract_config == '--psm 6'
            assert engine.batch_size == 5
            assert engine.enable_parallel is False
    
    def test_init_invalid_config(self):
        """Test OCREngine initialization with invalid config."""
        with pytest.raises(OCREngineError, match="Configuration must be a dictionary"):
            OCREngine("invalid_config")
    
    def test_init_missing_ocr_config(self):
        """Test OCREngine initialization with missing OCR config."""
        config = {'other_section': {}}
        with patch('ocr_receipt.core.ocr_engine.pytesseract.get_tesseract_version'):
            engine = OCREngine(config)
            
            # Should use defaults
            assert engine.language == 'eng'
            assert engine.confidence_threshold == 0.6
    
    def test_init_tesseract_not_available(self):
        """Test OCREngine initialization when Tesseract is not available."""
        config = {'ocr': {}}
        with patch('ocr_receipt.core.ocr_engine.pytesseract.get_tesseract_version',
                  side_effect=Exception("Tesseract not found")):
            with pytest.raises(OCREngineError, match="Tesseract OCR not available"):
                OCREngine(config)
    
    def test_validate_pdf_file_exists(self, ocr_engine, mock_pdf_path):
        """Test PDF validation when file exists."""
        with patch('os.path.exists', return_value=True), \
             patch('os.access', return_value=True), \
             patch('ocr_receipt.core.ocr_engine.convert_from_path', return_value=[Mock()]):
            
            result = ocr_engine.validate_pdf_file(mock_pdf_path)
            assert result is True
    
    def test_validate_pdf_file_not_exists(self, ocr_engine, mock_pdf_path):
        """Test PDF validation when file does not exist."""
        with patch('os.path.exists', return_value=False):
            result = ocr_engine.validate_pdf_file(mock_pdf_path)
            assert result is False
    
    def test_validate_pdf_file_not_readable(self, ocr_engine, mock_pdf_path):
        """Test PDF validation when file is not readable."""
        with patch('os.path.exists', return_value=True), \
             patch('os.access', return_value=False):
            result = ocr_engine.validate_pdf_file(mock_pdf_path)
            assert result is False
    
    def test_validate_pdf_file_wrong_extension(self, ocr_engine):
        """Test PDF validation when file has wrong extension."""
        result = ocr_engine.validate_pdf_file("/path/to/file.txt")
        assert result is False
    
    def test_get_pdf_page_count_success(self, ocr_engine, mock_pdf_path):
        """Test getting PDF page count successfully."""
        mock_images = [Mock(), Mock(), Mock()]  # 3 pages
        
        with patch.object(ocr_engine, 'validate_pdf_file', return_value=True), \
             patch('ocr_receipt.core.ocr_engine.convert_from_path', return_value=mock_images):
            
            page_count = ocr_engine.get_pdf_page_count(mock_pdf_path)
            assert page_count == 3
    
    def test_get_pdf_page_count_invalid_pdf(self, ocr_engine, mock_pdf_path):
        """Test getting PDF page count with invalid PDF."""
        with patch.object(ocr_engine, 'validate_pdf_file', return_value=False):
            with pytest.raises(OCREngineError, match="Invalid or inaccessible PDF file"):
                ocr_engine.get_pdf_page_count(mock_pdf_path)
    
    def test_extract_text_from_pdf_page_success(self, ocr_engine, mock_pdf_path):
        """Test extracting text from a specific page successfully."""
        mock_image = Mock()
        mock_processed_image = Mock()
        mock_text = "Sample text from page"
        mock_confidence = 0.85
        
        with patch.object(ocr_engine, 'get_pdf_page_count', return_value=3), \
             patch('ocr_receipt.core.ocr_engine.convert_from_path', return_value=[mock_image]), \
             patch.object(ocr_engine, '_preprocess_image', return_value=mock_processed_image), \
             patch.object(ocr_engine, '_extract_text_from_image', return_value=(mock_text, mock_confidence)):
            
            text, confidence = ocr_engine.extract_text_from_pdf_page_with_confidence(mock_pdf_path, 1)
            
            assert text == mock_text
            assert confidence == mock_confidence
    
    def test_extract_text_from_pdf_page_invalid_page(self, ocr_engine, mock_pdf_path):
        """Test extracting text from invalid page number."""
        with patch.object(ocr_engine, 'get_pdf_page_count', return_value=3):
            with pytest.raises(OCREngineError, match="Invalid page number"):
                ocr_engine.extract_text_from_pdf_page_with_confidence(mock_pdf_path, 5)
    
    def test_extract_text_from_pdf_page_conversion_fails(self, ocr_engine, mock_pdf_path):
        """Test extracting text when PDF to image conversion fails."""
        with patch.object(ocr_engine, 'get_pdf_page_count', return_value=3), \
             patch('ocr_receipt.core.ocr_engine.convert_from_path', return_value=[]):
            
            with pytest.raises(OCREngineError, match="Failed to convert page"):
                ocr_engine.extract_text_from_pdf_page_with_confidence(mock_pdf_path, 1)
    
    def test_extract_text_from_all_pages_success(self, ocr_engine, mock_pdf_path):
        """Test extracting text from all pages successfully."""
        mock_images = [Mock(), Mock()]  # 2 pages
        mock_processed_image = Mock()
        mock_text1 = "Text from page 1"
        mock_text2 = "Text from page 2"
        mock_confidence1 = 0.8
        mock_confidence2 = 0.9
        
        with patch.object(ocr_engine, 'validate_pdf_file', return_value=True), \
             patch.object(ocr_engine, 'get_pdf_page_count', return_value=2), \
             patch('ocr_receipt.core.ocr_engine.convert_from_path', return_value=mock_images), \
             patch.object(ocr_engine, '_preprocess_image', return_value=mock_processed_image), \
             patch.object(ocr_engine, '_extract_text_from_image', side_effect=[
                 (mock_text1, mock_confidence1), (mock_text2, mock_confidence2)
             ]):
            
            results = ocr_engine.extract_text_from_all_pages(mock_pdf_path)
            
            assert len(results) == 2
            assert results[0] == (1, mock_text1, mock_confidence1)
            assert results[1] == (2, mock_text2, mock_confidence2)
    
    def test_extract_text_from_all_pages_with_failures(self, ocr_engine, mock_pdf_path):
        """Test extracting text from all pages with some page failures."""
        mock_images = [Mock(), Mock()]  # 2 pages
        mock_processed_image = Mock()
        mock_text1 = "Text from page 1"
        mock_confidence1 = 0.8
        
        with patch.object(ocr_engine, 'validate_pdf_file', return_value=True), \
             patch.object(ocr_engine, 'get_pdf_page_count', return_value=2), \
             patch('ocr_receipt.core.ocr_engine.convert_from_path', return_value=mock_images), \
             patch.object(ocr_engine, '_preprocess_image', return_value=mock_processed_image), \
             patch.object(ocr_engine, '_extract_text_from_image', side_effect=[
                 (mock_text1, mock_confidence1), Exception("Page 2 failed")
             ]):
            
            results = ocr_engine.extract_text_from_all_pages(mock_pdf_path)
            
            assert len(results) == 2
            assert results[0] == (1, mock_text1, mock_confidence1)
            assert results[1] == (2, "", 0.0)  # Failed page
    
    def test_extract_text_from_pdf_success(self, ocr_engine, mock_pdf_path):
        """Test extracting text from entire PDF successfully."""
        mock_pages_data = [
            (1, "Text from page 1", 0.8),
            (2, "Text from page 2", 0.9)
        ]
        
        with patch.object(ocr_engine, 'extract_text_from_all_pages', return_value=mock_pages_data):
            text = ocr_engine.extract_text_from_pdf(mock_pdf_path)
            
            expected_text = "--- Page 1 ---\nText from page 1\n\n--- Page 2 ---\nText from page 2"
            assert text == expected_text
    
    def test_extract_text_from_pdf_with_confidence_success(self, ocr_engine, mock_pdf_path):
        """Test extracting text with confidence from entire PDF successfully."""
        mock_pages_data = [
            (1, "Text from page 1", 0.8),
            (2, "Text from page 2", 0.9)
        ]
        
        with patch.object(ocr_engine, 'extract_text_from_all_pages', return_value=mock_pages_data):
            text, confidence = ocr_engine.extract_text_from_pdf_with_confidence(mock_pdf_path)
            
            expected_text = "--- Page 1 ---\nText from page 1\n\n--- Page 2 ---\nText from page 2"
            expected_confidence = 0.85  # Average of 0.8 and 0.9
            
            assert text == expected_text
            assert abs(confidence - expected_confidence) < 0.001
    
    def test_extract_text_from_pdf_with_confidence_empty_pages(self, ocr_engine, mock_pdf_path):
        """Test extracting text with confidence when no pages are processed."""
        with patch.object(ocr_engine, 'extract_text_from_all_pages', return_value=[]):
            text, confidence = ocr_engine.extract_text_from_pdf_with_confidence(mock_pdf_path)
            
            assert text == ""
            assert confidence == 0.0
    
    def test_get_confidence_scores_success(self, ocr_engine, mock_pdf_path):
        """Test getting confidence scores successfully."""
        mock_pages_data = [
            (1, "Text from page 1", 0.8),
            (2, "Text from page 2", 0.9)
        ]
        
        with patch.object(ocr_engine, 'extract_text_from_all_pages', return_value=mock_pages_data):
            confidence_scores = ocr_engine.get_confidence_scores(mock_pdf_path)
            
            assert confidence_scores == [0.8, 0.9]
    
    def test_get_page_confidence_scores_success(self, ocr_engine, mock_pdf_path):
        """Test getting page confidence scores successfully."""
        mock_pages_data = [
            (1, "Text from page 1", 0.8),
            (2, "Text from page 2", 0.9)
        ]
        
        with patch.object(ocr_engine, 'extract_text_from_all_pages', return_value=mock_pages_data):
            page_confidence_scores = ocr_engine.get_page_confidence_scores(mock_pdf_path)
            
            assert page_confidence_scores == [(1, 0.8), (2, 0.9)]
    
    def test_is_confidence_acceptable_above_threshold(self, ocr_engine):
        """Test confidence acceptability when above threshold."""
        assert ocr_engine.is_confidence_acceptable(0.8) is True
    
    def test_is_confidence_acceptable_below_threshold(self, ocr_engine):
        """Test confidence acceptability when below threshold."""
        assert ocr_engine.is_confidence_acceptable(0.4) is False
    
    def test_is_confidence_acceptable_at_threshold(self, ocr_engine):
        """Test confidence acceptability when at threshold."""
        assert ocr_engine.is_confidence_acceptable(0.6) is True
    
    @patch('ocr_receipt.core.ocr_engine.cv2')
    @patch('ocr_receipt.core.ocr_engine.np')
    def test_preprocess_image_success(self, mock_np, mock_cv2, ocr_engine):
        """Test image preprocessing successfully."""
        # Mock image
        mock_image = Mock()
        mock_image.shape = (200, 300, 3)  # RGB image
        
        # Mock numpy array
        mock_array = Mock()
        mock_array.shape = (200, 300, 3)
        mock_np.array.return_value = mock_array
        
        # Mock OpenCV operations
        mock_gray = Mock()
        mock_gray.shape = (200, 300)
        mock_cv2.cvtColor.return_value = mock_gray
        mock_cv2.resize.return_value = mock_gray
        mock_cv2.GaussianBlur.return_value = mock_gray
        mock_cv2.threshold.return_value = (None, mock_gray)
        
        result = ocr_engine._preprocess_image(mock_image)
        
        assert result == mock_gray
        mock_np.array.assert_called_once_with(mock_image)
    
    @patch('ocr_receipt.core.ocr_engine.cv2')
    @patch('ocr_receipt.core.ocr_engine.np')
    def test_preprocess_image_small_image(self, mock_np, mock_cv2, ocr_engine):
        """Test image preprocessing with small image (should resize)."""
        # Mock image
        mock_image = Mock()
        mock_image.shape = (50, 50, 3)  # Small RGB image
        
        # Mock numpy array
        mock_array = Mock()
        mock_array.shape = (50, 50, 3)
        mock_np.array.return_value = mock_array
        
        # Mock OpenCV operations
        mock_gray = Mock()
        mock_gray.shape = (50, 50)
        mock_cv2.cvtColor.return_value = mock_gray
        mock_cv2.resize.return_value = mock_gray
        mock_cv2.GaussianBlur.return_value = mock_gray
        mock_cv2.threshold.return_value = (None, mock_gray)
        
        result = ocr_engine._preprocess_image(mock_image)
        
        # Should call resize for small image
        mock_cv2.resize.assert_called()
        assert result == mock_gray
    
    def test_preprocess_image_failure(self, ocr_engine):
        """Test image preprocessing when it fails."""
        mock_image = Mock()
        mock_image.shape = (200, 300, 3)
        
        # Mock np.array to fail on first call but succeed on second call (fallback)
        with patch('ocr_receipt.core.ocr_engine.np.array', side_effect=[Exception("Processing failed"), Mock()]):
            result = ocr_engine._preprocess_image(mock_image)
            
            # Should return original image if preprocessing fails
            assert result is not None
    
    @patch('ocr_receipt.core.ocr_engine.pytesseract')
    @patch('ocr_receipt.core.ocr_engine.Image')
    def test_extract_text_from_image_success(self, mock_pil_image, mock_pytesseract, ocr_engine):
        """Test text extraction from image successfully."""
        # Mock image
        mock_image = Mock()
        mock_image.shape = (200, 300)
        
        # Mock PIL Image
        mock_pil_instance = Mock()
        mock_pil_image.fromarray.return_value = mock_pil_instance
        
        # Mock pytesseract
        mock_data = {
            'conf': ['90', '85', '95', '0', '88']  # Some valid, some invalid confidences
        }
        mock_pytesseract.image_to_data.return_value = mock_data
        mock_pytesseract.image_to_string.return_value = "Extracted text"
        
        text, confidence = ocr_engine._extract_text_from_image(mock_image)
        
        assert text == "Extracted text"
        assert confidence > 0.0  # Should be average of valid confidences
        mock_pytesseract.image_to_data.assert_called_once()
        mock_pytesseract.image_to_string.assert_called_once()
    
    @patch('ocr_receipt.core.ocr_engine.pytesseract')
    @patch('ocr_receipt.core.ocr_engine.Image')
    def test_extract_text_from_image_no_valid_confidence(self, mock_pil_image, mock_pytesseract, ocr_engine):
        """Test text extraction when no valid confidence scores."""
        # Mock image
        mock_image = Mock()
        mock_image.shape = (200, 300)
        
        # Mock PIL Image
        mock_pil_instance = Mock()
        mock_pil_image.fromarray.return_value = mock_pil_instance
        
        # Mock pytesseract with no valid confidences
        mock_data = {
            'conf': ['0', '-1', '0', '0']  # All invalid confidences
        }
        mock_pytesseract.image_to_data.return_value = mock_data
        mock_pytesseract.image_to_string.return_value = "Extracted text"
        
        text, confidence = ocr_engine._extract_text_from_image(mock_image)
        
        assert text == "Extracted text"
        assert confidence == 0.0  # Should be 0 when no valid confidences
    
    def test_extract_text_from_image_failure(self, ocr_engine):
        """Test text extraction when it fails."""
        mock_image = Mock()
        
        with patch('ocr_receipt.core.ocr_engine.Image.fromarray', side_effect=Exception("Extraction failed")):
            text, confidence = ocr_engine._extract_text_from_image(mock_image)
            
            assert text == ""
            assert confidence == 0.0 
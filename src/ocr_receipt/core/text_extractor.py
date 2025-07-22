"""
Text Extractor module for PDF processing.

This module provides high-level text extraction functionality for PDF files,
coordinating between OCR engine and image processing components.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional

from .ocr_engine import OCREngine, OCREngineError
from .image_processor import ImageProcessor, ImageProcessorError

logger = logging.getLogger(__name__)


class TextExtractorError(Exception):
    """Exception raised for text extraction errors."""
    pass


class TextExtractor:
    """
    Extract and process text from PDF files.
    
    This class provides high-level text extraction functionality,
    coordinating between OCR engine and image processing components
    for optimal text extraction from PDF files.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the text extractor.
        
        Args:
            config: Configuration dictionary containing extraction settings
        """
        self.config = config
        self._validate_config()
        
        # Initialize components
        self.ocr_engine = OCREngine(config)
        self.image_processor = ImageProcessor(config)
        
        # Extraction settings
        extract_config = self.config.get('text_extraction', {})
        self.enable_preprocessing = extract_config.get('enable_preprocessing', True)
        self.enable_enhancement = extract_config.get('enable_enhancement', False)
        self.min_confidence = extract_config.get('min_confidence', 0.6)
        self.max_retries = extract_config.get('max_retries', 3)
        
        logger.info("Text Extractor initialized")
    
    def _validate_config(self) -> None:
        """Validate the configuration."""
        if not isinstance(self.config, dict):
            raise TextExtractorError("Configuration must be a dictionary")
        
        extract_config = self.config.get('text_extraction', {})
        if not isinstance(extract_config, dict):
            raise TextExtractorError("Text extraction configuration must be a dictionary")
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from all pages of a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Combined text from all pages
            
        Raises:
            TextExtractorError: If text extraction fails
        """
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            # Use OCR engine for text extraction
            text = self.ocr_engine.extract_text_from_pdf(pdf_path)
            
            logger.info(f"Successfully extracted text from PDF: {pdf_path}")
            return text
            
        except OCREngineError as e:
            logger.error(f"OCR engine error during text extraction: {e}")
            raise TextExtractorError(f"OCR engine error: {e}")
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")
            raise TextExtractorError(f"Failed to extract text from PDF: {e}")
    
    def extract_from_pdf_page(self, pdf_path: str, page_number: int) -> str:
        """
        Extract text from a specific page of a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            page_number: Page number (1-based)
            
        Returns:
            Text extracted from the specified page
            
        Raises:
            TextExtractorError: If text extraction fails
        """
        try:
            logger.info(f"Extracting text from page {page_number} of PDF: {pdf_path}")
            
            # Use OCR engine for page-specific text extraction
            text = self.ocr_engine.extract_text_from_pdf_page(pdf_path, page_number)
            
            logger.info(f"Successfully extracted text from page {page_number}")
            return text
            
        except OCREngineError as e:
            logger.error(f"OCR engine error during page text extraction: {e}")
            raise TextExtractorError(f"OCR engine error: {e}")
        except Exception as e:
            logger.error(f"Failed to extract text from page {page_number} of PDF {pdf_path}: {e}")
            raise TextExtractorError(f"Failed to extract text from page {page_number}: {e}")
    
    def extract_from_pdf_with_confidence(self, pdf_path: str) -> Tuple[str, float]:
        """
        Extract text from all pages of a PDF file with overall confidence score.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (combined_text, overall_confidence)
            
        Raises:
            TextExtractorError: If text extraction fails
        """
        try:
            logger.info(f"Extracting text with confidence from PDF: {pdf_path}")
            
            # Use OCR engine for text extraction with confidence
            text, confidence = self.ocr_engine.extract_text_from_pdf_with_confidence(pdf_path)
            
            logger.info(f"Successfully extracted text with confidence: {confidence:.2f}")
            return text, confidence
            
        except OCREngineError as e:
            logger.error(f"OCR engine error during text extraction with confidence: {e}")
            raise TextExtractorError(f"OCR engine error: {e}")
        except Exception as e:
            logger.error(f"Failed to extract text with confidence from PDF {pdf_path}: {e}")
            raise TextExtractorError(f"Failed to extract text with confidence from PDF: {e}")
    
    def extract_from_all_pages(self, pdf_path: str) -> List[Tuple[int, str, float]]:
        """
        Extract text from all pages of a PDF file with individual confidence scores.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of tuples (page_number, text, confidence) for each page
            
        Raises:
            TextExtractorError: If text extraction fails
        """
        try:
            logger.info(f"Extracting text from all pages of PDF: {pdf_path}")
            
            # Use OCR engine for all pages extraction
            pages_data = self.ocr_engine.extract_text_from_all_pages(pdf_path)
            
            logger.info(f"Successfully extracted text from {len(pages_data)} pages")
            return pages_data
            
        except OCREngineError as e:
            logger.error(f"OCR engine error during all pages text extraction: {e}")
            raise TextExtractorError(f"OCR engine error: {e}")
        except Exception as e:
            logger.error(f"Failed to extract text from all pages of PDF {pdf_path}: {e}")
            raise TextExtractorError(f"Failed to extract text from all pages: {e}")
    
    def extract_with_retry(self, pdf_path: str, max_retries: Optional[int] = None) -> str:
        """
        Extract text from PDF with retry logic for better results.
        
        Args:
            pdf_path: Path to the PDF file
            max_retries: Maximum number of retry attempts (uses config default if None)
            
        Returns:
            Best text extraction result
            
        Raises:
            TextExtractorError: If all retry attempts fail
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        best_text = ""
        best_confidence = 0.0
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Text extraction attempt {attempt + 1}/{max_retries + 1}")
                
                # Extract text with confidence
                text, confidence = self.extract_from_pdf_with_confidence(pdf_path)
                
                # Update best result if confidence is higher
                if confidence > best_confidence:
                    best_text = text
                    best_confidence = confidence
                    logger.info(f"New best result with confidence: {confidence:.2f}")
                
                # If confidence is acceptable, return early
                if confidence >= self.min_confidence:
                    logger.info(f"Acceptable confidence achieved: {confidence:.2f}")
                    return text
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries:
                    raise TextExtractorError(f"All retry attempts failed: {e}")
        
        logger.info(f"Returning best result with confidence: {best_confidence:.2f}")
        return best_text
    
    def extract_page_with_retry(self, pdf_path: str, page_number: int, max_retries: Optional[int] = None) -> str:
        """
        Extract text from a specific page with retry logic.
        
        Args:
            pdf_path: Path to the PDF file
            page_number: Page number (1-based)
            max_retries: Maximum number of retry attempts (uses config default if None)
            
        Returns:
            Best text extraction result for the page
            
        Raises:
            TextExtractorError: If all retry attempts fail
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        best_text = ""
        best_confidence = 0.0
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Page {page_number} text extraction attempt {attempt + 1}/{max_retries + 1}")
                
                # Extract text with confidence from specific page
                text, confidence = self.ocr_engine.extract_text_from_pdf_page_with_confidence(pdf_path, page_number)
                
                # Update best result if confidence is higher
                if confidence > best_confidence:
                    best_text = text
                    best_confidence = confidence
                    logger.info(f"New best result for page {page_number} with confidence: {confidence:.2f}")
                
                # If confidence is acceptable, return early
                if confidence >= self.min_confidence:
                    logger.info(f"Acceptable confidence achieved for page {page_number}: {confidence:.2f}")
                    return text
                
            except Exception as e:
                logger.warning(f"Page {page_number} attempt {attempt + 1} failed: {e}")
                if attempt == max_retries:
                    raise TextExtractorError(f"All retry attempts failed for page {page_number}: {e}")
        
        logger.info(f"Returning best result for page {page_number} with confidence: {best_confidence:.2f}")
        return best_text
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF information
            
        Raises:
            TextExtractorError: If PDF processing fails
        """
        try:
            logger.info(f"Getting PDF info for: {pdf_path}")
            
            # Validate PDF file
            if not self.ocr_engine.validate_pdf_file(pdf_path):
                raise TextExtractorError(f"Invalid or inaccessible PDF file: {pdf_path}")
            
            # Get page count
            page_count = self.ocr_engine.get_pdf_page_count(pdf_path)
            
            # Get confidence scores for all pages
            confidence_scores = self.ocr_engine.get_confidence_scores(pdf_path)
            
            # Calculate overall confidence
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # Get page confidence scores with page numbers
            page_confidence_scores = self.ocr_engine.get_page_confidence_scores(pdf_path)
            
            info = {
                'file_path': pdf_path,
                'page_count': page_count,
                'overall_confidence': overall_confidence,
                'page_confidence_scores': page_confidence_scores,
                'confidence_scores': confidence_scores,
                'is_valid': True
            }
            
            logger.info(f"PDF info retrieved: {page_count} pages, overall confidence: {overall_confidence:.2f}")
            return info
            
        except Exception as e:
            logger.error(f"Failed to get PDF info for {pdf_path}: {e}")
            raise TextExtractorError(f"Failed to get PDF info: {e}")
    
    def validate_extraction_quality(self, pdf_path: str) -> Dict[str, Any]:
        """
        Validate the quality of text extraction from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing quality assessment
            
        Raises:
            TextExtractorError: If quality validation fails
        """
        try:
            logger.info(f"Validating extraction quality for: {pdf_path}")
            
            # Get PDF info
            pdf_info = self.get_pdf_info(pdf_path)
            
            # Extract text from all pages
            pages_data = self.extract_from_all_pages(pdf_path)
            
            # Analyze quality metrics
            quality_metrics = {
                'total_pages': pdf_info['page_count'],
                'successful_pages': len([data for data in pages_data if data[2] > 0]),
                'failed_pages': len([data for data in pages_data if data[2] == 0]),
                'average_confidence': pdf_info['overall_confidence'],
                'min_confidence': min([data[2] for data in pages_data]) if pages_data else 0.0,
                'max_confidence': max([data[2] for data in pages_data]) if pages_data else 0.0,
                'acceptable_pages': len([data for data in pages_data if data[2] >= self.min_confidence]),
                'total_characters': sum(len(data[1]) for data in pages_data),
                'quality_score': 0.0
            }
            
            # Calculate quality score
            if quality_metrics['total_pages'] > 0:
                quality_metrics['quality_score'] = (
                    quality_metrics['acceptable_pages'] / quality_metrics['total_pages'] * 
                    quality_metrics['average_confidence']
                )
            
            logger.info(f"Quality validation completed: score {quality_metrics['quality_score']:.2f}")
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Failed to validate extraction quality for {pdf_path}: {e}")
            raise TextExtractorError(f"Failed to validate extraction quality: {e}") 
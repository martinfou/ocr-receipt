"""
OCR Engine module for PDF processing.

This module provides the main OCR functionality using Tesseract OCR
for processing PDF files with multi-page support and confidence scoring.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import tempfile

import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class OCREngineError(Exception):
    """Exception raised for OCR engine errors."""
    pass


class OCREngine:
    """
    OCR engine using Tesseract for PDF processing.
    
    This class provides comprehensive OCR functionality for PDF files,
    including multi-page support, confidence scoring, and error handling.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the OCR engine.
        
        Args:
            config: Configuration dictionary containing OCR settings
        """
        self.config = config
        self._validate_config()
        self._setup_tesseract()
        
        # OCR parameters
        self.language = self.config.get('ocr', {}).get('language', 'eng')
        self.confidence_threshold = self.config.get('ocr', {}).get('confidence_threshold', 0.6)
        self.tesseract_config = self.config.get('ocr', {}).get('tesseract_config', '--psm 6')
        
        # Performance settings
        self.batch_size = self.config.get('ocr', {}).get('batch_size', 5)
        self.enable_parallel = self.config.get('ocr', {}).get('enable_parallel', False)
        
        logger.info(f"OCR Engine initialized with language: {self.language}")
    
    def _validate_config(self) -> None:
        """Validate the configuration."""
        if not isinstance(self.config, dict):
            raise OCREngineError("Configuration must be a dictionary")
        
        ocr_config = self.config.get('ocr', {})
        if not isinstance(ocr_config, dict):
            raise OCREngineError("OCR configuration must be a dictionary")
    
    def _setup_tesseract(self) -> None:
        """Set up Tesseract OCR."""
        try:
            # Check if Tesseract is available
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
        except Exception as e:
            logger.error(f"Tesseract OCR not available: {e}")
            raise OCREngineError(f"Tesseract OCR not available: {e}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from all pages of a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Combined text from all pages
            
        Raises:
            OCREngineError: If PDF processing fails
        """
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            # Get all pages with confidence
            pages_data = self.extract_text_from_all_pages(pdf_path)
            
            # Combine text from all pages
            combined_text = "\n\n".join([f"--- Page {page_num} ---\n{text}" 
                                        for page_num, text, confidence in pages_data])
            
            logger.info(f"Successfully extracted text from {len(pages_data)} pages")
            return combined_text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")
            raise OCREngineError(f"Failed to extract text from PDF: {e}")
    
    def extract_text_from_pdf_with_confidence(self, pdf_path: str) -> Tuple[str, float]:
        """
        Extract text from all pages of a PDF file with overall confidence score.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (combined_text, overall_confidence)
            
        Raises:
            OCREngineError: If PDF processing fails
        """
        try:
            logger.info(f"Extracting text with confidence from PDF: {pdf_path}")
            
            # Get all pages with confidence
            pages_data = self.extract_text_from_all_pages(pdf_path)
            
            if not pages_data:
                return "", 0.0
            
            # Combine text from all pages
            combined_text = "\n\n".join([f"--- Page {page_num} ---\n{text}" 
                                        for page_num, text, confidence in pages_data])
            
            # Calculate overall confidence (average of all pages)
            overall_confidence = sum(confidence for _, _, confidence in pages_data) / len(pages_data)
            
            logger.info(f"Successfully extracted text from {len(pages_data)} pages with confidence: {overall_confidence:.2f}")
            return combined_text, overall_confidence
            
        except Exception as e:
            logger.error(f"Failed to extract text with confidence from PDF {pdf_path}: {e}")
            raise OCREngineError(f"Failed to extract text with confidence from PDF: {e}")
    
    def extract_text_from_pdf_page(self, pdf_path: str, page_number: int) -> str:
        """
        Extract text from a specific page of a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            page_number: Page number (1-based)
            
        Returns:
            Text extracted from the specified page
            
        Raises:
            OCREngineError: If page processing fails
        """
        try:
            logger.info(f"Extracting text from page {page_number} of PDF: {pdf_path}")
            
            text, _ = self.extract_text_from_pdf_page_with_confidence(pdf_path, page_number)
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract text from page {page_number} of PDF {pdf_path}: {e}")
            raise OCREngineError(f"Failed to extract text from page {page_number}: {e}")
    
    def extract_text_from_pdf_page_with_confidence(self, pdf_path: str, page_number: int) -> Tuple[str, float]:
        """
        Extract text from a specific page of a PDF file with confidence score.
        
        Args:
            pdf_path: Path to the PDF file
            page_number: Page number (1-based)
            
        Returns:
            Tuple of (text, confidence)
            
        Raises:
            OCREngineError: If page processing fails
        """
        try:
            logger.info(f"Extracting text with confidence from page {page_number} of PDF: {pdf_path}")
            
            # Validate page number
            total_pages = self.get_pdf_page_count(pdf_path)
            if page_number < 1 or page_number > total_pages:
                raise OCREngineError(f"Invalid page number {page_number}. PDF has {total_pages} pages.")
            
            # Convert PDF page to image
            images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number)
            if not images:
                raise OCREngineError(f"Failed to convert page {page_number} to image")
            
            image = images[0]
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text with confidence
            text, confidence = self._extract_text_from_image(processed_image)
            
            logger.info(f"Successfully extracted text from page {page_number} with confidence: {confidence:.2f}")
            return text, confidence
            
        except Exception as e:
            logger.error(f"Failed to extract text with confidence from page {page_number} of PDF {pdf_path}: {e}")
            raise OCREngineError(f"Failed to extract text with confidence from page {page_number}: {e}")
    
    def extract_text_from_all_pages(self, pdf_path: str) -> List[Tuple[int, str, float]]:
        """
        Extract text from all pages of a PDF file with individual confidence scores.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of tuples (page_number, text, confidence) for each page
            
        Raises:
            OCREngineError: If PDF processing fails
        """
        try:
            logger.info(f"Extracting text from all pages of PDF: {pdf_path}")
            
            # Validate PDF file
            if not self.validate_pdf_file(pdf_path):
                raise OCREngineError(f"Invalid or inaccessible PDF file: {pdf_path}")
            
            # Get total page count
            total_pages = self.get_pdf_page_count(pdf_path)
            logger.info(f"PDF has {total_pages} pages")
            
            # Convert all pages to images
            images = convert_from_path(pdf_path)
            
            if not images:
                raise OCREngineError("Failed to convert PDF to images")
            
            # Process each page
            results = []
            for page_num, image in enumerate(images, 1):
                try:
                    logger.debug(f"Processing page {page_num}/{total_pages}")
                    
                    # Preprocess image for better OCR
                    processed_image = self._preprocess_image(image)
                    
                    # Extract text with confidence
                    text, confidence = self._extract_text_from_image(processed_image)
                    
                    results.append((page_num, text, confidence))
                    logger.debug(f"Page {page_num} processed with confidence: {confidence:.2f}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process page {page_num}: {e}")
                    # Add empty result for failed page
                    results.append((page_num, "", 0.0))
            
            logger.info(f"Successfully processed {len(results)} pages")
            return results
            
        except Exception as e:
            logger.error(f"Failed to extract text from all pages of PDF {pdf_path}: {e}")
            raise OCREngineError(f"Failed to extract text from all pages: {e}")
    
    def get_pdf_page_count(self, pdf_path: str) -> int:
        """
        Get the total number of pages in a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Number of pages in the PDF
            
        Raises:
            OCREngineError: If PDF processing fails
        """
        try:
            logger.debug(f"Getting page count for PDF: {pdf_path}")
            
            # Validate PDF file
            if not self.validate_pdf_file(pdf_path):
                raise OCREngineError(f"Invalid or inaccessible PDF file: {pdf_path}")
            
            # Convert PDF to images to get page count
            images = convert_from_path(pdf_path)
            page_count = len(images)
            
            logger.debug(f"PDF has {page_count} pages")
            return page_count
            
        except Exception as e:
            logger.error(f"Failed to get page count for PDF {pdf_path}: {e}")
            raise OCREngineError(f"Failed to get page count: {e}")
    
    def validate_pdf_file(self, pdf_path: str) -> bool:
        """
        Validate that a PDF file exists and is accessible.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if PDF is valid and accessible, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(pdf_path):
                logger.warning(f"PDF file does not exist: {pdf_path}")
                return False
            
            # Check if file is readable
            if not os.access(pdf_path, os.R_OK):
                logger.warning(f"PDF file is not readable: {pdf_path}")
                return False
            
            # Check file extension
            if not pdf_path.lower().endswith('.pdf'):
                logger.warning(f"File does not have PDF extension: {pdf_path}")
                return False
            
            # Try to open with pdf2image to validate PDF format
            try:
                images = convert_from_path(pdf_path, first_page=1, last_page=1)
                if not images:
                    logger.warning(f"Failed to convert first page of PDF: {pdf_path}")
                    return False
            except Exception as e:
                logger.warning(f"PDF validation failed: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating PDF file {pdf_path}: {e}")
            return False
    
    def get_confidence_scores(self, pdf_path: str) -> List[float]:
        """
        Get confidence scores for all pages in a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of confidence scores for each page
            
        Raises:
            OCREngineError: If PDF processing fails
        """
        try:
            logger.info(f"Getting confidence scores for PDF: {pdf_path}")
            
            pages_data = self.extract_text_from_all_pages(pdf_path)
            confidence_scores = [confidence for _, _, confidence in pages_data]
            
            logger.info(f"Retrieved confidence scores for {len(confidence_scores)} pages")
            return confidence_scores
            
        except Exception as e:
            logger.error(f"Failed to get confidence scores for PDF {pdf_path}: {e}")
            raise OCREngineError(f"Failed to get confidence scores: {e}")
    
    def get_page_confidence_scores(self, pdf_path: str) -> List[Tuple[int, float]]:
        """
        Get confidence scores for all pages with page numbers.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of tuples (page_number, confidence) for each page
            
        Raises:
            OCREngineError: If PDF processing fails
        """
        try:
            logger.info(f"Getting page confidence scores for PDF: {pdf_path}")
            
            pages_data = self.extract_text_from_all_pages(pdf_path)
            page_confidence_scores = [(page_num, confidence) for page_num, _, confidence in pages_data]
            
            logger.info(f"Retrieved page confidence scores for {len(page_confidence_scores)} pages")
            return page_confidence_scores
            
        except Exception as e:
            logger.error(f"Failed to get page confidence scores for PDF {pdf_path}: {e}")
            raise OCREngineError(f"Failed to get page confidence scores: {e}")
    
    def is_confidence_acceptable(self, confidence: float) -> bool:
        """
        Check if a confidence score meets the threshold.
        
        Args:
            confidence: Confidence score to check
            
        Returns:
            True if confidence meets threshold, False otherwise
        """
        return confidence >= self.confidence_threshold
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess an image for better OCR results.
        
        Args:
            image: PIL Image to preprocess
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Convert PIL image to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply preprocessing techniques
            # 1. Resize if too small
            height, width = img_array.shape
            if height < 100 or width < 100:
                scale_factor = max(2, 100 / min(height, width))
                new_height = int(height * scale_factor)
                new_width = int(width * scale_factor)
                img_array = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # 2. Apply Gaussian blur to reduce noise
            img_array = cv2.GaussianBlur(img_array, (1, 1), 0)
            
            # 3. Apply thresholding to improve contrast
            _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return img_array
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            # Return original image if preprocessing fails
            return np.array(image)
    
    def _extract_text_from_image(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Extract text from a preprocessed image with confidence score.
        
        Args:
            image: Preprocessed image as numpy array
            
        Returns:
            Tuple of (text, confidence)
        """
        try:
            # Convert numpy array to PIL Image for pytesseract
            pil_image = Image.fromarray(image)
            
            # Extract text with confidence data
            data = pytesseract.image_to_data(
                pil_image, 
                lang=self.language, 
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text
            text = pytesseract.image_to_string(
                pil_image, 
                lang=self.language, 
                config=self.tesseract_config
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            if confidences:
                average_confidence = sum(confidences) / len(confidences) / 100.0  # Normalize to 0-1
            else:
                average_confidence = 0.0
            
            return text.strip(), average_confidence
            
        except Exception as e:
            logger.error(f"Text extraction from image failed: {e}")
            return "", 0.0 
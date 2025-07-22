"""
Image Processor module for PDF processing.

This module provides image processing functionality for PDF files,
including PDF to image conversion and image preprocessing for better OCR results.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile

from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessorError(Exception):
    """Exception raised for image processing errors."""
    pass


class ImageProcessor:
    """
    Process PDF pages for better OCR results.
    
    This class provides functionality for converting PDF pages to images
    and applying preprocessing techniques to improve OCR accuracy.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the image processor.
        
        Args:
            config: Configuration dictionary containing image processing settings
        """
        self.config = config
        self._validate_config()
        
        # Image processing parameters
        img_config = self.config.get('image_processing', {})
        self.dpi = img_config.get('dpi', 300)
        self.quality = img_config.get('quality', 95)
        self.format = img_config.get('format', 'PNG')
        
        # Preprocessing settings
        self.enable_noise_reduction = img_config.get('enable_noise_reduction', True)
        self.enable_contrast_enhancement = img_config.get('enable_contrast_enhancement', True)
        self.enable_deskew = img_config.get('enable_deskew', True)
        self.min_image_size = img_config.get('min_image_size', 100)
        
        logger.info(f"Image Processor initialized with DPI: {self.dpi}")
    
    def _validate_config(self) -> None:
        """Validate the configuration."""
        if not isinstance(self.config, dict):
            raise ImageProcessorError("Configuration must be a dictionary")
        
        img_config = self.config.get('image_processing', {})
        if not isinstance(img_config, dict):
            raise ImageProcessorError("Image processing configuration must be a dictionary")
    
    def convert_pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """
        Convert all pages of a PDF file to images.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of images as numpy arrays
            
        Raises:
            ImageProcessorError: If PDF conversion fails
        """
        try:
            logger.info(f"Converting PDF to images: {pdf_path}")
            
            # Validate PDF file
            if not self._validate_pdf_file(pdf_path):
                raise ImageProcessorError(f"Invalid or inaccessible PDF file: {pdf_path}")
            
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                fmt=self.format,
                quality=self.quality
            )
            
            if not images:
                raise ImageProcessorError("Failed to convert PDF to images")
            
            # Convert PIL images to numpy arrays
            numpy_images = []
            for i, image in enumerate(images):
                try:
                    numpy_image = np.array(image)
                    numpy_images.append(numpy_image)
                    logger.debug(f"Converted page {i+1} to image")
                except Exception as e:
                    logger.warning(f"Failed to convert page {i+1} to numpy array: {e}")
                    # Add empty image for failed page
                    numpy_images.append(np.zeros((100, 100, 3), dtype=np.uint8))
            
            logger.info(f"Successfully converted {len(numpy_images)} pages to images")
            return numpy_images
            
        except Exception as e:
            logger.error(f"Failed to convert PDF to images {pdf_path}: {e}")
            raise ImageProcessorError(f"Failed to convert PDF to images: {e}")
    
    def preprocess_pdf_page(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess a PDF page image for better OCR results.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            logger.debug("Preprocessing PDF page image")
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply preprocessing techniques
            processed_image = image.copy()
            
            # 1. Resize if too small
            processed_image = self._resize_if_needed(processed_image)
            
            # 2. Deskew if enabled
            if self.enable_deskew:
                processed_image = self._deskew_image(processed_image)
            
            # 3. Noise reduction if enabled
            if self.enable_noise_reduction:
                processed_image = self._reduce_noise(processed_image)
            
            # 4. Contrast enhancement if enabled
            if self.enable_contrast_enhancement:
                processed_image = self._enhance_contrast(processed_image)
            
            logger.debug("PDF page preprocessing completed")
            return processed_image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            # Return original image if preprocessing fails
            return image
    
    def enhance_pdf_page(self, image: np.ndarray) -> np.ndarray:
        """
        Apply advanced enhancement techniques to a PDF page image.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Enhanced image as numpy array
        """
        try:
            logger.debug("Enhancing PDF page image")
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            enhanced_image = image.copy()
            
            # 1. Apply adaptive histogram equalization
            enhanced_image = cv2.equalizeHist(enhanced_image)
            
            # 2. Apply morphological operations to clean up text
            kernel = np.ones((1, 1), np.uint8)
            enhanced_image = cv2.morphologyEx(enhanced_image, cv2.MORPH_CLOSE, kernel)
            
            # 3. Apply bilateral filter to preserve edges while smoothing
            enhanced_image = cv2.bilateralFilter(enhanced_image, 9, 75, 75)
            
            # 4. Apply adaptive thresholding
            enhanced_image = cv2.adaptiveThreshold(
                enhanced_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            logger.debug("PDF page enhancement completed")
            return enhanced_image
            
        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            # Return original image if enhancement fails
            return image
    
    def get_pdf_page_count(self, pdf_path: str) -> int:
        """
        Get the total number of pages in a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Number of pages in the PDF
            
        Raises:
            ImageProcessorError: If PDF processing fails
        """
        try:
            logger.debug(f"Getting page count for PDF: {pdf_path}")
            
            # Validate PDF file
            if not self._validate_pdf_file(pdf_path):
                raise ImageProcessorError(f"Invalid or inaccessible PDF file: {pdf_path}")
            
            # Convert PDF to images to get page count
            images = convert_from_path(pdf_path, dpi=self.dpi)
            page_count = len(images)
            
            logger.debug(f"PDF has {page_count} pages")
            return page_count
            
        except Exception as e:
            logger.error(f"Failed to get page count for PDF {pdf_path}: {e}")
            raise ImageProcessorError(f"Failed to get page count: {e}")
    
    def _validate_pdf_file(self, pdf_path: str) -> bool:
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
                images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=self.dpi)
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
    
    def _resize_if_needed(self, image: np.ndarray) -> np.ndarray:
        """
        Resize image if it's too small for OCR.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Resized image as numpy array
        """
        height, width = image.shape
        if height < self.min_image_size or width < self.min_image_size:
            scale_factor = max(2, self.min_image_size / min(height, width))
            new_height = int(height * scale_factor)
            new_width = int(width * scale_factor)
            return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        return image
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Deskew an image to correct rotation.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Deskewed image as numpy array
        """
        try:
            # Find contours
            contours, _ = cv2.findContours(
                cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
                cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            if not contours:
                return image
            
            # Find the largest contour (assumed to be the main content)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get the minimum area rectangle
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[2]
            
            # Adjust angle
            if angle < -45:
                angle = 90 + angle
            
            # Rotate image if angle is significant
            if abs(angle) > 0.5:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                return rotated
            
            return image
            
        except Exception as e:
            logger.warning(f"Deskewing failed: {e}")
            return image
    
    def _reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Reduce noise in an image.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Denoised image as numpy array
        """
        try:
            # Apply Gaussian blur to reduce noise
            return cv2.GaussianBlur(image, (1, 1), 0)
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance contrast in an image.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Contrast-enhanced image as numpy array
        """
        try:
            # Apply histogram equalization
            return cv2.equalizeHist(image)
        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {e}")
            return image 
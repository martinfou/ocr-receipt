"""
Core module for OCR Receipt Parser.

This module contains the core OCR functionality including:
- OCREngine: Main OCR engine using Tesseract
- ImageProcessor: PDF to image conversion and preprocessing
- TextExtractor: Text extraction from PDF files
- FuzzyMatcher: Fuzzy string matching utilities
"""

from .ocr_engine import OCREngine
from .image_processor import ImageProcessor
from .text_extractor import TextExtractor
from .fuzzy_matcher import FuzzyMatcher

__all__ = [
    'OCREngine',
    'ImageProcessor', 
    'TextExtractor',
    'FuzzyMatcher'
] 
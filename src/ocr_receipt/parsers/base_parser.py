"""
BaseParser: Common parsing functionality and validation for invoice and statement parsers.
"""
from typing import Dict, Any, Union
from pathlib import Path
from ocr_receipt.core.ocr_engine import OCREngine
from ocr_receipt.core.text_extractor import TextExtractor
from ocr_receipt.core.fuzzy_matcher import FuzzyMatcher

class BaseParser:
    """
    Base class for all parsers. Provides OCR, text extraction, and validation utilities.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the parser with configuration and core components.
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.ocr_engine = OCREngine(config)
        self.text_extractor = TextExtractor(config)
        self.fuzzy_matcher = FuzzyMatcher(self.config)

    def parse(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse PDF and return structured data. To be implemented by subclasses.
        Args:
            pdf_path: Path to the PDF file.
        Returns:
            Extracted data as a dictionary.
        """
        raise NotImplementedError("Subclasses must implement parse()")

    def extract_text(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract text from PDF using OCR.
        Args:
            pdf_path: Path to the PDF file.
        Returns:
            Extracted text as a string.
        """
        return self.text_extractor.extract_from_pdf(str(pdf_path))

    def validate_extraction_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and calculate confidence for extraction result.
        Args:
            result: Dictionary of extracted data.
        Returns:
            Validated result with confidence scores.
        """
        # Example: Add a confidence score if not present
        if "confidence" not in result:
            result["confidence"] = self._calculate_confidence(result)
        result["is_valid"] = self._validate_result(result)
        return result

    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Calculate a confidence score for the extraction result.
        Args:
            result: Dictionary of extracted data.
        Returns:
            Confidence score as a float between 0 and 1.
        """
        required_fields = ["company", "total", "date", "invoice_number"]
        if all(result.get(field) for field in required_fields):
            return 1.0
        return 0.5

    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate the extraction result for required fields and formats.
        Args:
            result: Dictionary of extracted data.
        Returns:
            True if valid, False otherwise.
        """
        # Placeholder: Subclasses can override for specific validation logic
        required_fields = ["company", "total", "date", "invoice_number"]
        return all(result.get(field) for field in required_fields) 
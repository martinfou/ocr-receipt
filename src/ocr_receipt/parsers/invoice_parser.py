"""
Invoice Parser module for extracting structured data from invoice PDFs.

This module provides functionality to extract company names, total amounts,
dates, and invoice numbers from invoice documents using OCR and text parsing.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from decimal import Decimal, InvalidOperation

from ocr_receipt.parsers.base_parser import BaseParser
from ocr_receipt.parsers.date_extractor import DateExtractor

logger = logging.getLogger(__name__)


class InvoiceParserError(Exception):
    """Exception raised for invoice parsing errors."""
    pass


class InvoiceParser(BaseParser):
    """
    Invoice parser for extracting structured data from invoice PDFs.
    
    This class provides functionality to extract:
    - Company name
    - Total amount
    - Invoice date
    - Invoice number
    
    from invoice documents using OCR and text parsing techniques.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the invoice parser.
        
        Args:
            config: Configuration dictionary containing parser settings
        """
        super().__init__(config)
        self.date_extractor = DateExtractor()
        
        # Common patterns for invoice data extraction
        self.company_patterns = [
            r'(?:company|business|vendor|from|bill\s+from|invoice\s+from|issued\s+by)[:\s]+([A-Za-z0-9\s&.,\-]+)',
            r'^([A-Za-z0-9\s&.,\-]+(?:\s+Inc\.|\s+LLC|\s+Ltd\.|\s+Corp\.|\s+Company))',
            r'([A-Za-z0-9\s&.,\-]+(?:\s+Inc\.|\s+LLC|\s+Ltd\.|\s+Corp\.|\s+Company))',
        ]
        
        self.total_patterns = [
            r'(?:total|amount|sum|balance|due|grand\s+total)[:\s]*[\$]?([\d,]+\.?\d*)',
            r'[\$]?([\d,]+\.?\d*)\s*(?:total|amount|sum|balance|due)',
            r'(?:amount\s+due|total\s+amount)[:\s]*[\$]?([\d,]+\.?\d*)',
            r'[\$]?([\d,]+\.?\d*)\s*(?:CAD|USD|EUR|GBP)',
        ]
        
        self.invoice_number_patterns = [
            r'(?:invoice\s+number|invoice\s+#|inv\s+number|inv\s+#|bill\s+number|bill\s+#)[:\s]*([A-Za-z0-9\-_]+)',
            r'(?:invoice|inv|bill)[:\s]*([A-Za-z0-9\-_]+)',
            r'([A-Za-z0-9\-_]+)\s*(?:invoice|inv|bill)',
        ]
        
        logger.info("InvoiceParser initialized")
    
    def parse(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Parse an invoice PDF and extract structured data.
        
        Args:
            pdf_path: Path to the invoice PDF file
            
        Returns:
            Dictionary containing extracted invoice data:
            {
                'company': str,
                'total': float,
                'date': str (ISO format),
                'invoice_number': str,
                'confidence': float,
                'is_valid': bool,
                'raw_text': str
            }
            
        Raises:
            InvoiceParserError: If parsing fails
        """
        try:
            # Extract text from PDF
            raw_text = self.extract_text(pdf_path)
            if not raw_text or not raw_text.strip():
                raise InvoiceParserError("No text extracted from PDF")
            
            # Extract individual components
            company = self._extract_company(raw_text)
            total = self._extract_total(raw_text)
            date = self._extract_date(raw_text)
            invoice_number = self._extract_invoice_number(raw_text)
            
            # Build result
            result = {
                'company': company,
                'total': total,
                'date': date,
                'invoice_number': invoice_number,
                'raw_text': raw_text,
                'pdf_path': str(pdf_path)
            }
            
            # Validate and add confidence scores
            validated_result = self.validate_extraction_result(result)
            
            logger.info(f"Successfully parsed invoice: {validated_result}")
            return validated_result
            
        except Exception as e:
            logger.error(f"Invoice parsing failed: {e}")
            raise InvoiceParserError(f"Invoice parsing failed: {e}")
    
    def _extract_company(self, text: str) -> Optional[str]:
        """
        Extract company name from text.
        
        Args:
            text: Text to search for company name
            
        Returns:
            Extracted company name or None if not found
        """
        try:
            # Try each pattern
            for pattern in self.company_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Clean up the match
                    company = matches[0].strip()
                    if len(company) > 2:  # Filter out very short matches
                        return company
            
            # Fallback: look for lines that might be company names
            lines = text.split('\n')
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if (len(line) > 3 and len(line) < 100 and 
                    re.match(r'^[A-Za-z0-9\s&.,\-]+$', line) and
                    not any(keyword in line.lower() for keyword in 
                           ['invoice', 'date', 'total', 'amount', 'number'])):
                    return line
            
            return None
            
        except Exception as e:
            logger.debug(f"Company extraction failed: {e}")
            return None
    
    def _extract_total(self, text: str) -> Optional[float]:
        """
        Extract total amount from text.
        
        Args:
            text: Text to search for total amount
            
        Returns:
            Extracted total amount as float or None if not found
        """
        try:
            # Try each pattern
            for pattern in self.total_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Clean up the match and convert to float
                    amount_str = matches[0].replace(',', '')
                    try:
                        amount = float(amount_str)
                        if amount > 0:  # Valid amount should be positive
                            return amount
                    except (ValueError, InvalidOperation):
                        continue
            
            # Fallback: look for currency patterns
            currency_pattern = r'[\$]?([\d,]+\.?\d*)'
            matches = re.findall(currency_pattern, text)
            if matches:
                # Try to find the largest amount (likely the total)
                amounts = []
                for match in matches:
                    try:
                        amount = float(match.replace(',', ''))
                        if 0 < amount < 1000000:  # Reasonable range
                            amounts.append(amount)
                    except (ValueError, InvalidOperation):
                        continue
                
                if amounts:
                    return max(amounts)  # Return the largest amount
            
            return None
            
        except Exception as e:
            logger.debug(f"Total extraction failed: {e}")
            return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """
        Extract invoice date from text.
        
        Args:
            text: Text to search for date
            
        Returns:
            Extracted date in ISO format (YYYY-MM-DD) or None if not found
        """
        try:
            return self.date_extractor.extract_date(text)
        except Exception as e:
            logger.debug(f"Date extraction failed: {e}")
            return None
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """
        Extract invoice number from text.
        
        Args:
            text: Text to search for invoice number
            
        Returns:
            Extracted invoice number or None if not found
        """
        try:
            # Try each pattern
            for pattern in self.invoice_number_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Clean up the match
                    invoice_num = matches[0].strip()
                    if len(invoice_num) > 0:
                        return invoice_num
            
            # Fallback: look for patterns that might be invoice numbers
            # Common patterns: INV-123, 12345, INV123, etc.
            fallback_patterns = [
                r'(?:INV|BILL|INVOICE)[\-\s]*([A-Za-z0-9\-_]+)',
                r'([A-Za-z0-9\-_]{3,20})\s*(?:invoice|inv|bill)',
                r'(?:number|#)[:\s]*([A-Za-z0-9\-_]{3,20})',
            ]
            
            for pattern in fallback_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    invoice_num = matches[0].strip()
                    if len(invoice_num) > 0:
                        return invoice_num
            
            return None
            
        except Exception as e:
            logger.debug(f"Invoice number extraction failed: {e}")
            return None
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the extraction result.
        
        Args:
            result: Dictionary of extracted data
            
        Returns:
            Confidence score as a float between 0 and 1
        """
        try:
            confidence = 0.0
            total_fields = 4
            
            # Company name confidence
            if result.get('company'):
                confidence += 0.25
                # Bonus for longer company names (more likely to be correct)
                if len(result['company']) > 5:
                    confidence += 0.05
            
            # Total amount confidence
            if result.get('total') and result['total'] > 0:
                confidence += 0.25
                # Bonus for reasonable amounts
                if 0.01 <= result['total'] <= 1000000:
                    confidence += 0.05
            
            # Date confidence
            if result.get('date'):
                confidence += 0.25
                # Bonus for valid ISO date
                if self.date_extractor.validate_date(result['date']):
                    confidence += 0.05
            
            # Invoice number confidence
            if result.get('invoice_number'):
                confidence += 0.25
                # Bonus for longer invoice numbers
                if len(result['invoice_number']) > 3:
                    confidence += 0.05
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.debug(f"Confidence calculation failed: {e}")
            return 0.0
    
    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate the extraction result for required fields and formats.
        
        Args:
            result: Dictionary of extracted data
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ['company', 'total', 'date', 'invoice_number']
            if not all(result.get(field) for field in required_fields):
                return False
            
            # Validate total amount
            if not isinstance(result['total'], (int, float)) or result['total'] <= 0:
                return False
            
            # Validate date format
            if not self.date_extractor.validate_date(result['date']):
                return False
            
            # Validate company name length
            if len(result['company']) < 2:
                return False
            
            # Validate invoice number length
            if len(result['invoice_number']) < 1:
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Result validation failed: {e}")
            return False 